#!/bin/ksh

echo "clean debug plugin"

if [[ -d $1 ]];then
	plugin_install_path=$1
else
	echo "Unknown plugin install path, abort"
	exit 0
fi

echo "Stopping debug process..."

for file in $plugin_install_path/external_plugins/$2/pid/*
do
    if test -f $file
    then
        pid=`cat $file`
        echo "Found PID file: $file"
        echo "PID to be killed: $pid"
        kill $pid
    fi
done

echo "Removing plugin directory..."

rm -rf $plugin_install_path

exit 0