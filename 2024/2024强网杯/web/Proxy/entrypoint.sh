#!/bin/sh

if [ ${ICQ_FLAG} ];then
    echo -n ${ICQ_FLAG} > /flag
    chown root:root /flag
    chmod 400 /flag
    echo [+] ICQ_FLAG OK
    unset ICQ_FLAG
else
    echo [!] no ICQ_FLAG
fi


nginx -g "daemon on;"

su app -c '
(cd /app && ./proxy&)
'

tail -f /dev/null