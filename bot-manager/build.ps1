python -m venv .venv
.venv\Scripts\activate

pip install -r requirements-prod.txt
pip install -r requirements-dev.txt

# flake8 ./app
black --check ./app
black ./app
isort ./app
pylint ./app
mypy ./app

# flake8 ./plugins
black --check ./plugins
black ./plugins
isort ./plugins
pylint ./plugins
mypy ./plugins

# flake8 ./profiles
black --check ./profiles
black ./profiles
isort ./profiles
pylint ./profiles
mypy ./profiles

pyinstaller --onedir start.py --name colabai --noconfirm

# --icon=icon.ico