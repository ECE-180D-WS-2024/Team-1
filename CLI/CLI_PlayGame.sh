#!/bin/bash

control_c() {
    echo "Killing background process"
    kill $PID
    exit
}

trap control_c SIGINT

cd BLE_Module
python BLE_Writer.py > BLE_Log.txt 2>&1 &
PID=$!
cd ..
python "Bomb_Goes_Boom.py"
kill $PID
exit