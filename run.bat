call .\.env\Scripts\activate.bat
python -c .\src\check_config.json .\src\excel_exporter.py -d .\configuration\
pause