# CS 224N Final Project (SQuAD)
Code for the Default Final Project (SQuAD) for [CS224N](http://web.stanford.edu/class/cs224n/), Winter 2018

## Team Members
Winston Wang, Michael Chung

## Setup Notes
1. Due to differences in environment preferences, make sure to include any `virtualenv` or iPython Notebook files in the `.gitignore`

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

