rem @echo off
@setlocal enabledelayedexpansion
cd /d %~dp0
git pull
echo %~dp0
echo %*%
set group=chichichi
set branch=develop
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
echo update output\!group!_!branch!
if not exist output\!group!_!branch!\.git (	rmdir /s /q output\!group!_!branch!)
if not exist output\!group!_!branch! (
	git lfs install
	git clone -b !branch! https://!username!:!password!@git.fantablade.cn/FantaBlade/!group!/excel_origin.git output\!group!_!branch!
)
cd output\!group!_!branch!
git stash
git clean -df
git fetch
git reset origin/!branch! --hard
git submodule update --init

echo update output\client_zh_cn\lua
if not exist output\client_zh_cn\lua\.git (	rmdir /s /q output\client_zh_cn\lua)
if not exist output\client_zh_cn\lua (
	git lfs install
	git clone -b !branch!_client https://!username!:!password!@git.fantablade.cn/FantaBlade/!group!/config_sheets.git output\client_zh_cn\lua
)
cd output\client_zh_cn\lua
git stash
git clean -df
git fetch
git reset origin/!branch!_client --hard
cd ../../..

echo update output\server_zh_cn\lua
if not exist output\server_zh_cn\lua\.git (	rmdir /s /q output\server_zh_cn\lua)
if not exist output\server_zh_cn\lua (
	git lfs install
	git clone -b !branch!_server https://!username!:!password!@git.fantablade.cn/FantaBlade/!group!/config_sheets.git output\server_zh_cn\lua
)
cd output\server_zh_cn\lua
git stash
git clean -df
git fetch
git reset origin/!branch!_server --hard
cd ../../..

copy ..\..\configuration_tmp\* .
python excel_exporter/main.py -c excel_exporter/excel_exporter/check_config.json -d ../../configuration_tmp/

echo %errorlevel%
if %errorlevel% neq 0 (
  echo 同步失败!
) else (
	git add .
	git commit -am "%message%"
	git rev-parse --short HEAD > ../version
	set /P commitid=<../version

	cd output\client_zh_cn\lua
	git add .
	git commit -am "%commitid% %message%"
	git push origin !branch!_client
	cd ../../..

	cd output\server_zh_cn\lua
	git add .
	git commit -am "%commitid% %message%"
	git push origin !branch!_server
	cd ../../..

	git push origin !branch!

	DEL /F /Q ../../configuration_tmp
	echo 完成!
)
pause
