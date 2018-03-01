# CS 224N Final Project (SQuAD)
Code for the Default Final Project (SQuAD) for [CS224N](http://web.stanford.edu/class/cs224n/), Winter 2018

## Team Members
Winston Wang, Michael Chung

## Setup Notes
1. Due to differences in environment preferences, make sure to include any `virtualenv` or iPython Notebook files in the `.gitignore`
2. Add the following lines to your `~/.bash_profile`:
    * `alias venv_create='virtualenv .env'`
    * `alias venv_start='source .env/bin/activate'`
    * `alias get_tf='pip install --upgrade tensorflow'`
    * `alias squad='cd ~/Stanford/CS224Nproject'`
    * `alias squad-activate='venv_start && source activate squad'`
3. Execute the following commands:
	* `venv_create` - create a new virtualenv
	* `venv_start` - activate the virtualenv
	* `get_tf` - import tensorflow into the virtualenv
	* `./get_started.sh` - imports a bunch of stuff
		* if you get an error halfway through saying it couldn't find `nltk` or something, make sure that line 5 of `requirements.txt` is `tensorflow=1.4.1` if you're on your local machine, or `tensorflow-gpu=1.4.1` if you're on the VM. Then run `./get_started.sh` again
	* `squad-activate` - activates the virtualenv and the conda `squad` environment

## Running
To run an experiment:
1. Navigate to the project home directory by executing `squad`
2. Start a new tmux process with an appropriate name (see [`tmux` commands](#`tmux`-commands))
3. Execute `squad-activate`
4. Execute `python main.py --experiment_name=<NAME> --mode=train`

To monitor via Tensorboard:
1. If you're still in the previous tmux environment, detach

## `tmux` commands
* `tmux new -s <NAME>` - creates a new process called <NAME>

## IMPORTANT
If you ever try to push and it tells you that you can't because some files are too large, follow these instructions:
* `git reset HEAD^` - removes the last commit (presumably the first commit to include the large files), but keeps all your changes
* carefully check the error message to see which files are too large, and add them to `.gitignore`

(Instructions adapted from https://sethrobertson.github.io/GitFixUm/fixup.html)

## Azure Notes
**username:** squires

**password:** coding4Jesus

### Starting the VM
1. Click "All resources" (in the left sidebar) from your Azure homepage
2. Click "cs224n-dev"
3. Click the "Start" button, wait for it to start
4. Click "Connect" (might have to reload the page for it to un-gray)
5. Copy paste the `ssh` command into your terminal
6. DON'T FORGET TO STOP THE VM WHEN YOU'RE DONE. JUST PRESS THE STOP BUTTON.
*Note: the IP seems to change every time you start the VM, so don't bother making an alias to `ssh` in or anything. Just copy-paste the command each time.*

### Inside the VM
* The VM is connected to my Github account, and our repo is cloned in `~/cs224n-project`.
* For super-convenience, I set up an alias to the `.bash_profile` so you can just type `squad` and it'll `cd` you into the repo.

### Updating VM's copy of code
To update the VM's copy of our code, just use `git pull` from the `cs224n-project` directory! No need for SCP or any of that mess.

