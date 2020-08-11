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
