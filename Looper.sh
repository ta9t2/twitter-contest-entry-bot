#!/bin/bash

function countdown() {
  secs=$((2 * 60 * 60))
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
  python3 EntryBot.py

  echo 'waiting...'
  countdown

  python3 UnfollowBot.py

  echo 'waiting...'
  countdown

  echo 'mv result files & marge'
  mkdir result_files
  mv result_*.csv result_files/
  cat result_files/result_EntryBot_*.csv > result_files/result_all_EntryBot.csv
  cat result_files/result_UnfollowBot_*.csv > result_files/result_all_UnfollowBot.csv
  cat result_files/result_DestroyAllFriendshipsBot_*.csv > result_files/result_all_DestroyAllFriendshipsBot.csv
done
