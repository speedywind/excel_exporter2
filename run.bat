call .\.env\Scripts\activate.bat
python .\src\excel_exporter.py -c .\src\check_config.json -d .\configuration\
pause