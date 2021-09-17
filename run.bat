rem @echo off
@setlocal enabledelayedexpansion
cd /d %~dp0
git pull
echo %~dp0
echo %*%
if exist configuration_tmp (
	DEL /F /Q configuration_tmp
)
md configuration_tmp

:param
set file=%1
if !file!A == A (
	goto end
) else (
	set hasInput="1"
)
shift /0
echo !file!
copy !file! configuration_tmp
goto param
:end

if not exist output (
	md output
)
call .\.env\Scripts\activate.bat
if !hasInput!A NEQ A (
	python .\main.py -c .\excel_exporter\check_config.json -d .\configuration_tmp\
) else (
	python .\main.py -c .\excel_exporter\check_config.json -d .\configuration\
)
if exist ..\WaterGun\Assets\LuaFramework\Lua\properties (
	copy output\client_zh_cn\lua\*.lua ..\WaterGun\Assets\LuaFramework\Lua\properties
	echo "rsync to ..\WaterGun\Assets\LuaFramework\Lua\properties"
)
pause