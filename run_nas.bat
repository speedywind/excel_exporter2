call .\.env\Scripts\activate.bat
python .\src\excel_exporter.py -c ^
    "\\NAS\Project\Water Gun\产品文档\设计文件\WaterGun-v0.1\check_config.json" ^
    "\\NAS\Project\Water Gun\产品文档\设计文件\WaterGun-v0.1\2.2water_gun_export_battle.xlsx" ^
    "\\NAS\Project\Water Gun\产品文档\设计文件\WaterGun-v0.1\2.3water_gun_export_grow_up.xlsx" ^
    "\\NAS\Project\Water Gun\产品文档\设计文件\WaterGun-v0.1\2.4water_gun_export_rogue_like.xlsx" ^
    "\\NAS\Project\Water Gun\产品文档\设计文件\WaterGun-v0.1\2.5water_gun_export_drama.xlsx" ^
    "\\NAS\Project\Water Gun\产品文档\设计文件\WaterGun-v0.1\2.6water_gun_export_function.xlsx" ^
pause