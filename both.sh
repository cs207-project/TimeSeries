#!/bin/bash
trap 'kill $(jobs -p)' EXIT
export PYTHONPATH=.
./go_server.py &
sleep .5 && ./go_client.py &
while :
do
  sleep 1
done
