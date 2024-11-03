python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install pyinstaller
pip install -r requirements.txt  # Assuming you have a requirements file
pyinstaller start.py

pyinstaller --onedir start.py