chcp 65001

:loop
    mkdir log
    mkdir result

    python tb_search_contests.py
    python tb_enter_contests.py
    timeout /T 7200 /NOBREAK

    python tb_unfollow.py
    timeout /T 7200 /NOBREAK

goto :loop

exit
