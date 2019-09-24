#!/bin/bash

function countdown() {
  secs=$((4 * 60 * 60))
  while [ $secs -gt 0 ]; do
    h=$(($secs / 3600))
    m=$(($secs % 3600 / 60))
    s=$(($secs % 60))
    echo -ne "$((h))h$(($m))m$(($s))s\033[0K\r"
    sleep 1
    secs=$(($secs-1))
  done
}

while : ; do
  mkdir log
  mkdir result

  python3 tb_search_contests.py
  echo 'waiting...'
  countdown

  python3 tb_enter_contests.py
  echo 'waiting...'
  countdown

  python3 tb_unfollow.py
  echo 'waiting...'
  countdown

done

exit
