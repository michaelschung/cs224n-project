# Copyright 2018 Stanford University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This file contains some basic model components"""

import tensorflow as tf
from tensorflow.python.ops.rnn_cell import DropoutWrapper
from tensorflow.python.ops import variable_scope as vs
from tensorflow.python.ops import rnn_cell


class RNNEncoder(object):
    """
    General-purpose module to encode a sequence using a RNN.
    It feeds the input through a RNN and returns all the hidden states.

    Note: In lecture 8, we talked about how you might use a RNN as an "encoder"
    to get a single, fixed size vector representation of a sequence
    (e.g. by taking element-wise max of hidden states).
    Here, we're using the RNN as an "encoder" but we're not taking max;
    we're just returning all the hidden states. The terminology "encoder"
    still applies because we're getting a different "encoding" of each
    position in the sequence, and we'll use the encodings downstream in the model.

    This code uses a bidirectional GRU, but you could experiment with other types of RNN.
    """

    def __init__(self, hidden_size, keep_prob, use_lstm, use_cpu):
        """
        Inputs:
          hidden_size: int. Hidden size of the RNN
          keep_prob: Tensor containing a single scalar that is the keep probability (for dropout)
        """
        self.hidden_size = hidden_size
        self.keep_prob = keep_prob
        self.rnn_cell_fw = rnn_cell.LSTMCell(self.hidden_size) if use_lstm else rnn_cell.GRUCell(self.hidden_size)
        self.rnn_cell_fw = DropoutWrapper(self.rnn_cell_fw, input_keep_prob=self.keep_prob)
        self.rnn_cell_bw = rnn_cell.LSTMCell(self.hidden_size) if use_lstm else rnn_cell.GRUCell(self.hidden_size)
        self.rnn_cell_bw = DropoutWrapper(self.rnn_cell_bw, input_keep_prob=self.keep_prob)
        self.use_cpu = use_cpu

    def build_graph(self, inputs, masks):
        """
        Inputs:
          inputs: Tensor shape (batch_size, seq_len, input_size)
          masks: Tensor shape (batch_size, seq_len).
            Has 1s where there is real input, 0s where there's padding.
            This is used to make sure tf.nn.bidirectional_dynamic_rnn doesn't iterate through masked steps.

        Returns:
          out: Tensor shape (batch_size, seq_len, hidden_size*2).
            This is all hidden states (fw and bw hidden states are concatenated).
        """
        with vs.variable_scope("RNNEncoder"):
            input_lens = tf.reduce_sum(masks, reduction_indices=1) # shape (batch_size)

            # Note: fw_out and bw_out are the hidden states for every timestep.
            # Each is shape (batch_size, seq_len, hidden_size).
            (fw_out, bw_out), _ = tf.nn.bidirectional_dynamic_rnn(self.rnn_cell_fw, self.rnn_cell_bw, inputs, input_lens, dtype=tf.float32, swap_memory=self.use_cpu)

            # Concatenate the forward and backward hidden states
            out = tf.concat([fw_out, bw_out], 2)

            # Apply dropout
            out = tf.nn.dropout(out, self.keep_prob)

            return out


class SimpleSoftmaxLayer(object):
    """
    Module to take set of hidden states, (e.g. one for each context location),
    and return probability distribution over those states.
    """

    def __init__(self):
        pass

    def build_graph(self, inputs, masks):
        """
        Applies one linear downprojection layer, then softmax.

        Inputs:
          inputs: Tensor shape (batch_size, seq_len, hidden_size)
          masks: Tensor shape (batch_size, seq_len)
            Has 1s where there is real input, 0s where there's padding.

        Outputs:
          logits: Tensor shape (batch_size, seq_len)
            logits is the result of the downprojection layer, but it has -1e30
            (i.e. very large negative number) in the padded locations
          prob_dist: Tensor shape (batch_size, seq_len)
            The result of taking softmax over logits.
            This should have 0 in the padded locations, and the rest should sum to 1.
        """
        with vs.variable_scope("SimpleSoftmaxLayer"):

            # Linear downprojection layer
            logits = tf.contrib.layers.fully_connected(inputs, num_outputs=1, activation_fn=None) # shape (batch_size, seq_len, 1)
            logits = tf.squeeze(logits, axis=[2]) # shape (batch_size, seq_len)

            # Take softmax over sequence
            masked_logits, prob_dist = masked_softmax(logits, masks, 1)

            return masked_logits, prob_dist

class BiDAF(object):
    """Module for bidirectional attention flow.

    Note: in this module we use the terminology of "keys" and "values" (see lectures).
    In the terminology of "X attends to Y", "keys attend to values".

    In the baseline model, the keys are the context hidden states
    and the values are the question hidden states.

    We choose to use general terminology of keys and values in this module
    (rather than context and question) to avoid confusion if you reuse this
    module with other inputs.
    """

    def __init__(self, keep_prob, key_vec_size, value_vec_size, reduce_mode, use_biases):
        """
        Inputs:
          keep_prob: tensor containing a single scalar that is the keep probability (for dropout)
          key_vec_size: size of the key vectors. int
          value_vec_size: size of the value vectors. int
        """
        self.keep_prob = keep_prob
        self.key_vec_size = key_vec_size
        self.value_vec_size = value_vec_size
        self.reduce_mode = reduce_mode
        self.use_biases = use_biases

    def build_graph(self, values, values_mask, keys):
        """
        Keys attend to values.
        For each key, return an attention distribution and an attention output vector.

        Inputs:
          values: Tensor shape (batch_size, num_values, value_vec_size).
          values_mask: Tensor shape (batch_size, num_values).
            1s where there's real input, 0s where there's padding
          keys: Tensor shape (batch_size, num_keys, value_vec_size)

        Outputs:
          attn_dist: Tensor shape (batch_size, num_keys, num_values).
            For each key, the distribution should sum to 1,
            and should be 0 in the value locations that correspond to padding.
          output: Tensor shape (batch_size, num_keys, hidden_size).
            This is the attention output; the weighted sum of the values
            (using the attention distribution as weights).
        """
        with vs.variable_scope("BiDAF"):
            ##### =====Calculate C2Q Attention===== #####
            w1_T = tf.get_variable('w1_T', shape=(1, self.key_vec_size), initializer=tf.contrib.layers.xavier_initializer())
            w2_T = tf.get_variable('w2_T', shape=(1, self.key_vec_size), initializer=tf.contrib.layers.xavier_initializer())
            w3_T = tf.get_variable('w3_T', shape=(1, self.key_vec_size), initializer=tf.contrib.layers.xavier_initializer())

            num_keys = keys.get_shape()[1].value
            num_values = values.get_shape()[1].value

            if self.use_biases:
                s1_bias = tf.get_variable('s1_bias', shape=(1, num_keys, self.value_vec_size), initializer=tf.zeros_initializer())
                s2_bias = tf.get_variable('s2_bias', shape=(1, self.value_vec_size, num_values), initializer=tf.zeros_initializer())
                s3_bias = tf.get_variable('s3_bias', shape=(1, num_keys, num_values), initializer=tf.zeros_initializer())
                # # shape (1, num_keys, value_vec_size)
                # c2q_bias = tf.get_variable('c2q_bias', shape=(1, 1, self.value_vec_size), initializer=tf.zeros_initializer())
                # # shape (1, 1, value_vec_size)
                # q2c_bias = tf.get_variable('q2c_bias', shape=(1, 1, self.value_vec_size), initializer=tf.zeros_initializer())

            s1 = tf.multiply(w1_T, keys, name='s1') # shape (batch_size, num_keys, value_vec_size)
            s2 = tf.transpose(tf.multiply(w2_T, values, name='s2'), perm=[0, 2, 1]) # shape (batch_size, value_vec_size, num_values)
            values_T = tf.transpose(values, perm=[0, 2, 1], name='values_T') # shape (batch_size, value_vec_size, num_values)
            s3 = tf.matmul(tf.multiply(w3_T, keys), values_T, name='s3') # shape (batch_size, num_keys, num_values)

            if self.use_biases:
                s1 += s1_bias
                s2 += s2_bias
                s3 += s3_bias

            # s1: shape (batch_size, num_keys, 1)
            # s2: shape (batch_size, 1, num_values)
            if self.reduce_mode == 0:
                s1_reduced = tf.expand_dims(s1[:, :, 1], 2)
                s2_reduced = tf.expand_dims(s2[:, 1, :], 1)
            elif self.reduce_mode == 1:
                s1_reduced = tf.expand_dims(tf.reduce_sum(s1, 2), 2)
                s2_reduced = tf.expand_dims(tf.reduce_sum(s2, 1), 1)
            else:
                s1_reduced = tf.expand_dims(tf.reduce_mean(s1, 2), 2)
                s2_reduced = tf.expand_dims(tf.reduce_mean(s2, 1), 1)

            S = s1_reduced + s2_reduced + s3 # shape (batch_size, num_keys, num_values)

            S_mask = tf.expand_dims(values_mask, 1, name='S_mask') # shape (batch_size, 1, num_values)
            _, attn_dist = masked_softmax(S, S_mask, 2) # shape (batch_size, num_keys, num_values). take softmax over values
            c2q_output = tf.matmul(attn_dist, values, name='c2q_output') # shape (batch_size, num_keys, value_vec_size)

            ##### =====Calculate Q2C Attention===== #####
            m = tf.reduce_max(S, axis=2, name='m') # shape (batch_size, num_keys)
            beta = tf.nn.softmax(m, name='beta')
            q2c_output = tf.matmul(tf.expand_dims(beta, 1), keys, name='q2c_output') # shape (batch_size, 1, value_vec_size)
            
            # shape (batch_size, num_keys, 8*hidden_size)
            output = tf.concat([keys, c2q_output, tf.multiply(keys, c2q_output), tf.multiply(keys, q2c_output)], axis=2)
            output = tf.nn.dropout(output, self.keep_prob, name='output')

            return attn_dist, output

class BasicAttn(object):
    """Module for basic attention.

    Note: in this module we use the terminology of "keys" and "values" (see lectures).
    In the terminology of "X attends to Y", "keys attend to values".

    In the baseline model, the keys are the context hidden states
    and the values are the question hidden states.

    We choose to use general terminology of keys and values in this module
    (rather than context and question) to avoid confusion if you reuse this
    module with other inputs.
    """

    def __init__(self, keep_prob, key_vec_size, value_vec_size):
        """
        Inputs:
          keep_prob: tensor containing a single scalar that is the keep probability (for dropout)
          key_vec_size: size of the key vectors. int
          value_vec_size: size of the value vectors. int
        """
        self.keep_prob = keep_prob
        self.key_vec_size = key_vec_size
        self.value_vec_size = value_vec_size

    def build_graph(self, values, values_mask, keys):
        """
        Keys attend to values.
        For each key, return an attention distribution and an attention output vector.

        Inputs:
          values: Tensor shape (batch_size, num_values, value_vec_size).
          values_mask: Tensor shape (batch_size, num_values).
            1s where there's real input, 0s where there's padding
          keys: Tensor shape (batch_size, num_keys, value_vec_size)

        Outputs:
          attn_dist: Tensor shape (batch_size, num_keys, num_values).
            For each key, the distribution should sum to 1,
            and should be 0 in the value locations that correspond to padding.
          output: Tensor shape (batch_size, num_keys, hidden_size).
            This is the attention output; the weighted sum of the values
            (using the attention distribution as weights).
        """
        with vs.variable_scope("BasicAttn"):

            # Calculate attention distribution
            values_t = tf.transpose(values, perm=[0, 2, 1]) # (batch_size, value_vec_size, num_values)
            attn_logits = tf.matmul(keys, values_t) # shape (batch_size, num_keys, num_values)
            attn_logits_mask = tf.expand_dims(values_mask, 1) # shape (batch_size, 1, num_values)
            _, attn_dist = masked_softmax(attn_logits, attn_logits_mask, 2) # shape (batch_size, num_keys, num_values). take softmax over values

            # Use attention distribution to take weighted sum of values
            output = tf.matmul(attn_dist, values) # shape (batch_size, num_keys, value_vec_size)

            # Apply dropout
            output = tf.nn.dropout(output, self.keep_prob)

            return attn_dist, output

        
class AddInput(object):
    """Module for additional features appended onto the word vectors
    Combines word vectors, exact match, token features, and aligned question embedding
    """

    def __init__(self, idf):
        """
        Inputs:
          idf: vector of idf frequencies.  Each column is a word
        """
        self.idf = idf####

    def build_graph(self, context_wv, qn_wv, context_ids, qn_ids):
        """
        Keys attend to values.
        For each context, append additional features

        Inputs:
          context_wv: tensor of shape (batch_size, context_len, embedding_size)
          qn_wv: tensor of shape (batch_size, question_len, embedding_size)
          context_ids: tensor of shape (batch_size, context_len)
          qn_ids: tensor of shape (batch_size, question_len)

        Outputs:
          context_emb: Tensor shape (batch_size, context_len, embedding_size+add_feat_size)
        """
        with vs.variable_scope("AddInput"):
            #find exact match
            
            #find POS
            
            #find NER
            
            #find the tfidf values for each word
            y, idx, count = tf.unique_with_counts(context_wv)
            ys = tf.gather(y, idx)
            idfs = tf.gather(self.idf, ys)
            counts = tf.gather(count, idx)
            tfidf = tf.divide(counts, idfs) #(batch_size, context_len)
            
            #find aligned question embedding
            
            context_emb = tf.concat([context_wv, tfidf], axis = 2) #(batch_size, context_len, embedding_size+1)
            print context_wv.shape, context_emb.shape
            return context_emb
        
class CharCNN(object):
    "Module for adding character-level CNNs outputs to the word vectors"
    def __init__(self, keep_prob, context_len, question_len, word_len, filters, kernel_size, char_embed_size, char_vocab):
        self.keep_prob = keep_prob
        self.context_len = context_len
        self.question_len = question_len
        self.word_len = word_len
        self.filters = filters
        self.kernel_size = kernel_size
        self.char_embed_size = char_embed_size
        self.char_vocab_len = len(char_vocab) + 2
    
    def conv_layer(self, char_embs, max_len):
        conv = tf.layers.conv1d(char_embs, self.filters, self.kernel_size, padding="SAME", name="conv")
        pool = tf.layers.max_pooling1d(conv, self.word_len, 1)
        conv_reshape = tf.reshape(pool, (-1, max_len, 1, self.filters))
        conv_squeeze = tf.squeeze(conv_reshape, axis = 2)
        return conv_squeeze
    
    def build_graph(self, context_embs, qn_embs, context_char_ids, qn_char_ids):
        char_embeddings = tf.get_variable("char_embeddings", shape = (self.char_vocab_len, self.char_embed_size), initializer = tf.contrib.layers.xavier_initializer(), dtype = tf.float32)
        
        # convolutions
        with tf.variable_scope("context"):
            context_char_embs = tf.reshape(tf.nn.embedding_lookup(char_embeddings, context_char_ids), (-1, self.word_len, self.char_embed_size))
            context_conv_temp = tf.layers.conv1d(context_char_embs, self.filters, self.kernel_size, padding="SAME", name="context_conv")
            context_pool = tf.layers.max_pooling1d(context_conv_temp, self.word_len, 1)
            context_conv_reshape = tf.reshape(context_pool, (-1, self.context_len, 1, self.filters))
            context_conv = tf.squeeze(context_conv_reshape, axis = 2)
        with tf.variable_scope("qn"):
            qn_char_embs = tf.reshape(tf.nn.embedding_lookup(char_embeddings, qn_char_ids), (-1, self.word_len, self.char_embed_size))
            qn_conv_temp = tf.layers.conv1d(qn_char_embs, self.filters, self.kernel_size, padding="SAME", name="qn_conv")
            qn_pool = tf.layers.max_pooling1d(qn_conv_temp, self.word_len, 1)
            qn_conv_reshape = tf.reshape(qn_pool, (-1, self.question_len, 1, self.filters))
            qn_conv = tf.squeeze(qn_conv_reshape, axis = 2)

        # append word vectors
        context_embs = tf.concat([context_embs, context_conv], axis = -1)
        qn_embs = tf.concat([qn_embs, qn_conv], axis = -1)
        
        return context_embs, qn_embs
        
def masked_softmax(logits, mask, dim):
    """
    Takes masked softmax over given dimension of logits.

    Inputs:
      logits: Numpy array. We want to take softmax over dimension dim.
      mask: Numpy array of same shape as logits.
        Has 1s where there's real data in logits, 0 where there's padding
      dim: int. dimension over which to take softmax

    Returns:
      masked_logits: Numpy array same shape as logits.
        This is the same as logits, but with 1e30 subtracted
        (i.e. very large negative number) in the padding locations.
      prob_dist: Numpy array same shape as logits.
        The result of taking softmax over masked_logits in given dimension.
        Should be 0 in padding locations.
        Should sum to 1 over given dimension.
    """
    exp_mask = (1 - tf.cast(mask, 'float')) * (-1e30) # -large where there's padding, 0 elsewhere
    masked_logits = tf.add(logits, exp_mask) # where there's padding, set logits to -large
    prob_dist = tf.nn.softmax(masked_logits, dim)
    return masked_logits, prob_dist
