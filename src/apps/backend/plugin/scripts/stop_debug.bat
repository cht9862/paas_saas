@echo off
setlocal enabledelayedexpansion

echo "clean debug plugin"

if "%1"=="" (
	echo "Unknown plugin install path, abort"
	exit 0
) else (
	set plugin_install_path=%1
)

echo "Stopping debug process..."

for %%i in (%plugin_install_path%\external_plugins\%2\pid\*.pid) do (
	for /f %%j in (%%i) do (
		set pid=%%j
		echo "Found PID file: %%i"
		echo "PID to be killed: %%j"
		taskkill /F /PID !pid!))

echo "Removing plugin directory..."
echo Y | rd /S %plugin_install_path%
exit 0