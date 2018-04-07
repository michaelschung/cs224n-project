# CS 224N Final Project (SQuAD)
Code for the Default Final Project (SQuAD) for [CS224N](http://web.stanford.edu/class/cs224n/), Winter 2018

### Team Members
Winston Wang, Michael Chung

## Contents
[Setup](#setup)

[Running](#running)

[Making Improvements](#making-improvements)

[`tmux`](#tmux-commands)

[Handling Large Files](#handling-large-files)

[Azure](#azure)

[CodaLab](#codalab)

[Experiments](#experiments)

[Citations](#citations)

## Setup
1. Due to differences in environment preferences, make sure to include any `virtualenv` or iPython Notebook files in the `.gitignore`
2. Add the following lines to your `~/.bash_profile`:
    * `alias venv_create='virtualenv .env'`
    * `alias venv_start='source .env/bin/activate'`
    * `alias get_tf='pip install --upgrade tensorflow'`
    * `alias squad='cd ~/Stanford/CS224Nproject'`
    * `alias squad-activate='venv_start && source activate squad'`
3. Reload your .bash_profile configuration by executing `. ~/.bash_profile`
4. Execute the following commands:
	* `venv_create` - create a new virtualenv
	* `venv_start` - activate the virtualenv
	* `get_tf` - import tensorflow into the virtualenv
	* `./get_started.sh` - imports a bunch of stuff
		* if you get an error halfway through saying it couldn't find `nltk` or something, make sure that line 5 of `requirements.txt` is `tensorflow=1.4.1` if you're on your local machine, or `tensorflow-gpu=1.4.1` if you're on the VM. Then run `./get_started.sh` again
	* `squad-activate` - activates the virtualenv and the conda `squad` environment

## Running
To run an experiment:
1. Navigate to the project home directory by executing `squad`
2. Start a new tmux session with an appropriate name (see [`tmux` commands](#tmux-commands))
3. Execute `squad-activate`
4. Execute `python main.py --experiment_name=<NAME> --mode=train`

To monitor via Tensorboard:
1. If you're still in the previous tmux environment, detach
2. Start a new tmux session with an appropriate name (e.g., 'tensorboard')
3. Navigate to the `experiments` directory
4. Execute `tensorboard --logdir=. --port=5678`
	* If you're training locally, you can now go to http://localhost:5678/
	* If you're training on the VM, execute `ssh -N -f -L localhost:1234:localhost:5678 squires@<IP>` (<IP> is the same one you used to ssh into the VM) from your local machine, and then go to http://localhost:1234/

## Making Improvements
Protocol for making new improvements:
1. Create a new branch with a descriptive branch name
2. Create a new flag under the `#improvments` section in `main.py` that turns improvement on or off
3. Create any new flags under the `#hyperparameters` section in `main.py` that are relevant to the improvement
4. Make sure to test carefully before merging branch

## tmux commands
* `tmux new -s <NAME>` - creates new session called <NAME>
* CMD-B-D - detach from current session
* `tmux a -t <NAME>` - attach to session called <NAME>
* `tmux ls` - list all sessions
* `tmux kill-session -t <NAME>` - kill session called <NAME>

## HANDLING LARGE FILES
If you ever try to push and it tells you that you can't because some files are too large, follow these instructions:
* `git reset HEAD^` - removes the last commit (presumably the first commit to include the large files), but keeps all your changes
* carefully check the error message to see which files are too large, and add them to `.gitignore`

(Instructions adapted from https://sethrobertson.github.io/GitFixUm/fixup.html)

## Azure
**username:** squires

**password:** [[REDACTED]]

### Starting the VM
1. Click "All resources" (in the left sidebar) from your Azure homepage
2. Click "cs224n-dev"
3. Click the "Start" button, wait for it to start
4. Click "Connect" (might have to reload the page for it to un-gray)
5. Copy paste the `ssh` command into your terminal
6. DON'T FORGET TO STOP THE VM WHEN YOU'RE DONE. JUST PRESS THE STOP BUTTON.
*Note: the IP seems to change every time you start the VM, so don't bother making an alias to `ssh` in or anything. Just copy-paste the command each time.*

### Inside the VM
* The VM is connected to Michael's Github account (michaelschung), and the repo is cloned in `~/cs224n-project`.
* For super-convenience, I set up an alias in `~/.bash_profile` so you can just type `squad` and it'll `cd` you into the repo.

### Updating VM's copy of code
For most things, to update the VM's copy of our code, just use `git pull` from the `cs224n-project` directory! No need for SCP or any of that mess.

The only case for using SCP would be for moving around large files.

Local to remote:
`scp [-r] <FILE/FOLDER> squires@<IP>:cs224n-project`
* Include the `-r` flag for folders
* `<IP>` is the one you used to ssh into the VM
* Feel free to append a more specific path

## CodaLab
Winston: wwang13

Michael: mchung96

Group name: cs224n-squires2

Worksheet: cs224n-squires

## Experiments
| # | **Name** | **Date** | **Best Dev EM (best checkpoint)** | **Best Dev F1 (iterations)** | Notes | New best? |
| - | -------- | -------- | ---------------------------- | ---------------------------- | ----- | --------- |
| 1 | baseline | 3/1/18 | 0.2934 (11.5k) | 0.4050 (16k) | default | Y |
| 2 | lstm | 3/10/18 | 0.3077 (14.5k) | 0.4182 (16k) | using LSTM (instead of GRU) cells in RNN | Y |
| 3 | bidaf | 3/18/18 | 0.3217 (18.5k) | 0.4426 (18.5k) | BiDAF using slice, concat3, and no dropout | Y |
| 4 | bidaf_rdcsm_cnct3_drpt | 3/19/18 | (terminated) | (terminated) | BiDAF using reduce_sum, concat3, and dropout | N |
| 5 | bidaf_rdcsm_cnct4_drpt | 3/19/18 | 0.3412 (12.5k) | 0.4598 (14.5k) | BiDAF using reduce_sum, concat4, and dropout | Y |
| 6 | bidaf_modelinglayer | 3/19/18 | (paused) | (paused) | experiment #5 with modeling layer (utilizes CPU, so about 25% slower) | (paused) |
| 7 | bidaf_modelinglayer_reducedhidden | 3/19/18 | 0.5025 (9.5k) | 0.6509 (9.5k) | lowered hidden size for modeling layer from 200 to 20 (50 broke after 2323 iterations) | Y |
| 8 | l2_endonstart | 3/19/18 | 0.5074 (13k) | 0.6580 (13.5k) | experiment #7 with l2=0.0001, end_on_start | Y |
| 9 | bidaf_biases | 3/20/18 | (terminated) | (terminated) | experiment #8 with biases added to outputs in the BiDAF layer | N |
| 10 | char_cnn | 3/20/18 | (paused) | (paused) | experiment #8 with character_cnn=True, batch_size=80 | (paused) |
| 11 | l2_endonstart_lr0005 | 3/20/18 | (paused) | (paused) | experiment #8 with learning_rate=0.0005 | (paused) |
| 12 | l2_endonstart_lr0001 | 3/20/18 | (terminated) | (terminated) | experiment #8 with learning_rate=0.0001 | (accidentally deleted data, but definitely wasn't better) |
| 13 | bidaf_sbiases | 3/20/18 | (terminated) | (terminated) | experiment #8 with biases added to s1/s2/s3 in the BiDAF layer | (terminated) |
| 14 | cnn_grumodeling | 3/20/18 | (running) | (running) | experiment #10 with modeling layer using GRUs instead of RNNs | (running) |
| 15 | grumodeling_embedsize200 | 3/21/18 | (terminated) | (terminated) | experiment #8 with modeling layer using GRUs, and embed_size=200 | (terminated) |
| 16 | l2_endonstart_new | 3/21/18 | (running) | (running) | re-run of experiment #8 for submitting | (running) |
| 17 | l2_endonstart_higherdropout | 3/21/18 | (running) | (running) | experiment #8 with dropout=0.3, l2=0.001, context_len=300, modeling_hidden_size=40 | (running) |
| 18 | tweak_params | 3/21/18 | (running) | (running) | experiment #8 with dropout=0.2, l2=0.0005, context_len=300, modeling_hidden_size=40 | (running) |

## Citations
1. Bird, Steven, Edward Loper and Ewan Klein (2009), Natural Language Processing with Python. O’Reilly Media Inc.
2. Danqi Chen, Adam Fisch, Jason Weston, and Antoine Bordes. Reading wikipedia to answer open-domain questions. arXiv preprint arXiv:1704.00051, 2017.
3. https://arxiv.org/pdf/1611.01603.pdf
