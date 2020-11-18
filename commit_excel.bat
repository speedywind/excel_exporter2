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
if exist output\configuration if not exist output\configuration\.git (
	DEL /F /Q output\configuration
)
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
cd ../..

echo update output\client\lua
if exist output\client\lua if not exist output\client\lua\.git (
	DEL /F /Q output\client\lua
)
if not exist output\client\lua (
	git lfs install
	git clone -b develop https://!username!:!password!@git.fantablade.cn/FantaBlade/WaterGun/config_sheets.git output\client\lua
)
cd output\client\lua
git stash
git clean -df
git fetch
git reset origin/develop --hard
cd ../../..

echo update output\server\lua
if exist output\server\lua if not exist output\server\lua (
	DEL /F /Q output\server\lua
)
if not exist output\server\lua (
	git lfs install
	git clone -b server https://!username!:!password!@git.fantablade.cn/FantaBlade/WaterGun/config_sheets.git output\server\lua
)
cd output\server\lua
git stash
git clean -df
git fetch
git reset origin/server --hard
cd ../../..

echo 开始导出配置
copy configuration_tmp\* output\configuration
python .\main.py -c .\excel_exporter\check_config.json -d .\configuration_tmp\

echo %errorlevel%
if %errorlevel% neq 0 (
  echo 同步失败!
  pause
  exit 1
)
cd output\configuration
git add .
git commit -am "%message%"
git rev-parse --short HEAD > ../version
set /P commitid=<../version
cd ../..

cd output\client\lua
git add .
git commit -am "%commitid% %message%"
git push origin develop
cd ../../..

cd output\server\lua
git add .
git commit -am "%commitid% %message%"
git push origin server
cd ../../..

cd output\configuration
git push origin develop
cd ../..

DEL /F /Q configuration_tmp
echo 同步完成!
pause