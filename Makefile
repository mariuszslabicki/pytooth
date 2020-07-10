build_venv: 
	PIPENV_VENV_IN_PROJECT="enabled" pipenv install
remove_env:
	pipenv --rm
run:
	pipenv run python3 run.py