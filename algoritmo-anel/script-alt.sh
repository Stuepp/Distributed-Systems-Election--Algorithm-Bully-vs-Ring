#!/bin/bash

if [ ! -d "log" ]
then
    mkdir log
fi

rm -r log/*

max_process=$1
leader=8
process=(1 4 6 2 12 5 14 20 21 7 11 27 18 23 24 16 15 29 25 9)
jobs=()

command="python3 anel-alt.py $leader $leader $max_process"
$command &
leader_job=$!

for i in $(seq 0 $(($max_process - 1))); do
    command="python3 anel-alt.py ${process[$i]} $leader $max_process"
    echo "$command"
    $command &
    jobs+=($!)
done

sleep 3
kill $leader_job
sleep 10

for i in ${jobs[@]}; do
    kill $i
done
