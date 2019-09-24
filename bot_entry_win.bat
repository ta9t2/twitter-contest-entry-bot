chcp 65001

:loop
    mkdir log
    mkdir result

    python tb_search_contests.py
    timeout /T 14400 /NOBREAK

    python tb_enter_contests.py
    timeout /T 14400 /NOBREAK

    python tb_unfollow.py
    timeout /T 14400 /NOBREAK

goto :loop

exit
