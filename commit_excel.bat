rem @echo off
@setlocal enabledelayedexpansion
cd /d %~dp0
git pull
echo %~dp0
echo %*%
if %1%A == A (
	set /p file=将NAS中的excel直接拖拽到此脚本上进行提交：
)
if exist configuration_tmp (
	DEL /F /Q configuration_tmp
)
md configuration_tmp

if !file!A NEQ A (
	echo !file!
	copy !file! configuration_tmp
	goto end
)
:param
set file=%1
if !file!A == A (
	goto end
)
shift /0
echo !file!
copy !file! configuration_tmp
goto param
:end

if not exist output (
	md output
)
if exist output/username (
	set /P username=<output/username
) else (
	set /p username=第一次启动请输入你的git账号，不是邮箱：
	echo !username!
	echo !username!>output/username
)

if exist output/password (
	set /P password=<output/password
) else (
	set /p password=第一次启动请输入你的git密码：
	echo !password!>output/password
)

set /p message=请输入本次的提交信息:
echo 更新所有仓库
echo update output\configuration
if not exist output\configuration\.git (	rmdir /s /q output\configuration)
if not exist output\configuration (
	git lfs install
	git clone -b develop https://!username!:!password!@git.fantablade.cn/FantaBlade/WaterGun/excel_origin.git output\configuration
)
cd output\configuration
git stash
git clean -df
git fetch
git reset origin/develop --hard
git submodule update

echo update output\client_zh_cn\lua
if not exist output\client_zh_cn\lua\.git (	rmdir /s /q output\client_zh_cn\lua)
if not exist output\client_zh_cn\lua (
	git lfs install
	git clone -b develop https://!username!:!password!@git.fantablade.cn/FantaBlade/WaterGun/config_sheets.git output\client_zh_cn\lua
)
cd output\client_zh_cn\lua
git stash
git clean -df
git fetch
git reset origin/develop --hard
cd ../../..

echo update output\server_zh_cn\lua
if not exist output\server_zh_cn\lua\.git (	rmdir /s /q output\server_zh_cn\lua)
if not exist output\server_zh_cn\lua (
	git lfs install
	git clone -b server https://!username!:!password!@git.fantablade.cn/FantaBlade/WaterGun/config_sheets.git output\server_zh_cn\lua
)
cd output\server_zh_cn\lua
git stash
git clean -df
git fetch
git reset origin/server --hard
cd ../../..

echo update output\client_zh_tw\lua
if not exist output\client_zh_tw\lua\.git (rmdir /s /q output\client_zh_tw\lua)
if not exist output\client_zh_tw\lua (
	git lfs install
	git clone -b develop_tw https://!username!:!password!@git.fantablade.cn/FantaBlade/WaterGun/config_sheets.git output\client_zh_tw\lua
)
cd output\client_zh_tw\lua
git stash
git clean -df
git fetch
git reset origin/develop_tw --hard
cd ../../..

echo update output\server_zh_tw\lua
if not exist output\server_zh_tw\lua\.git (rmdir /s /q output\server_zh_tw\lua)
if not exist output\server_zh_tw\lua (
	git lfs install
	git clone -b server_tw https://!username!:!password!@git.fantablade.cn/FantaBlade/WaterGun/config_sheets.git output\server_zh_tw\lua
)
cd output\server_zh_tw\lua
git stash
git clean -df
git fetch
git reset origin/server_tw --hard
cd ../../..

copy ..\..\configuration_tmp\* .
python excel_exporter/main.py -c excel_exporter/excel_exporter/check_config.json -d ../../configuration_tmp/

echo %errorlevel%
if %errorlevel% neq 0 (
  echo 同步失败!
  pause
  exit 1
)
git add .
git commit -am "%message%"
git rev-parse --short HEAD > ../version
set /P commitid=<../version

cd output\client_zh_cn\lua
git add .
git commit -am "%commitid% %message%"
git push origin develop
cd ../../..

cd output\server_zh_cn\lua
git add .
git commit -am "%commitid% %message%"
git push origin server
cd ../../..

cd output\client_zh_tw\lua
git add .
git commit -am "%commitid% %message%"
git push origin develop_tw
cd ../../..

cd output\server_zh_tw\lua
git add .
git commit -am "%commitid% %message%"
git push origin server_tw
cd ../../..

git push origin develop

DEL /F /Q ../../configuration_tmp
echo 完成!
pause
