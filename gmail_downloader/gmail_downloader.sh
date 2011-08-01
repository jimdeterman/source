#! /bin/bash

LAST_RUN_TIME=`cat /home/jim/bin/gmail_download_last_run`
date +'%d-%b-%Y' > /home/jim/bin/gmail_download_last_run
echo $LAST_RUN_TIME
/home/jim/bin/gmail_downloader.py --save-dir=/data/email/my.gmail.com/inbox --since="$LAST_RUN_TIME" --mailbox=INBOX --verbose --username='your.username' --password='your.password'
