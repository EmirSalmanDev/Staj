### Uygulama Derleme Adımları (Windows)
```bash
python -m venv venv
pip install -r requirements.txt
pyinstaller --clean --name=inventory_table --onefile --windowed --icon=atasay_icon.ico main.py
```

