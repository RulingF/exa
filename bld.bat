"%PYTHON%" setup.py install
jupyter nbextension install exatomic --py --sys-prefix --overwrite
jupyter nbextension enable exatomic --py --sys-prefix
if errorlevel 1 exit 1
