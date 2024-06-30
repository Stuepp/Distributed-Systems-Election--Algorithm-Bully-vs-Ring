#!/bin/bash

if [ ! -d "log" ]
then
    mkdir log
fi

rm -r log/*

process=(8 1 4 6 2 12 5)
jobs=()

for i in ${!process[@]}; do
    comand="python3 ring.py ${process[$i]} ${process[0]}"
    echo "$comand"
    $comand &
    jobs+=($!)
    echo "${jobs[$i]}"
done

sleep 3
kill ${jobs[0]}
sleep 10

for i in ${jobs[@]}; do
    kill $i
done
