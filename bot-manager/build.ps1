python -m venv .venv

.venv\Scripts\activate

pip install pyinstaller
pip install -r requirements-dev.txt
# pip install -r requirements-prod.txt

pyinstaller --onedir start.py