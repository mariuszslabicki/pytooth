# Pytooth
The easiest way to run this software is to install [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) to manage packets and
environemnts. If you don't believe in pipenv, you can install packages mentioned
in Pipfile.

If you have installed pipenv, clone the repo and:

```sh

$ cd pytooth
$ make build_env
$ make run

```

If you don't have pipenv, install packages and evaluate `python3 run.py`.

If you want to change network configuration, you can do that in `run.py` file.


##There are 2 files ready to work at WCSS:

`generate_files.py` is a script used to create folders stored the network definition for simulation; by default is it network.ini file
`run.py` main script used to start simulaiton process for network as defined in "network.ini".

###Examples:
`python3 generate_files.py main_experiment_define_file.ini`
will create many folders with parameters values in name and network.ini file in them (diffrent for diffrent folder)
`run.py network.ini` 
will start simulation process for one separte network definie in network.ini file and store output.json file as a simulaiton resoult.


 
