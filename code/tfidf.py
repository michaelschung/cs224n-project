from sklearn.feature_extraction.text import TfidfVectorizer
import time
import numpy as np


def get_tfidf(train_context_path, vocabulary):
    """
    Inputs:  path to contexts used for training
    Outputs: TF-IDF sparse matrix.  
        Each row corresponds to a document
        Each column corresponds to a word in the vocabulary
    Because the output is a sparse matrix, each row can be turned regular again by using
        row = np.squeeze(tfidf[row_num].toarray())
    Should never turn the sparse matrix into a dense matrix (too large)
    """
    print "Calculating TF-IDF frequencies..."
    start = time.time()
    tfidf_vect = TfidfVectorizer(vocabulary = vocabulary)
    with open(train_context_path, "r") as train_context:
        docs = train_context.read().split('\n')
    tfidf = tfidf_vect.fit_transform(docs)
    end = time.time()
    print "Calculating TF-IDF frequencies took  %f seconds"%(end-start)
    return tfidf