chcp 65001

:loop
    python EntryBot_enc.py
    timeout /T 7200 /NOBREAK

    python UnfollowBot_enc.py
    timeout /T 7200 /NOBREAK

    mkdir output_files
    move result_*.csv output_files
    copy /b output_files\result_EntryBot_*.csv output_files\result_all_EntryBot.csv
    copy /b output_files\result_UnfollowBot_*.csv output_files\result_all_UnfollowBot.csv
    copy /b output_files\result_DestroyAllFriendshipsBot_*.csv output_files\result_all_DestroyAllFriendshipsBot.csv
goto :loop

pause
exit
