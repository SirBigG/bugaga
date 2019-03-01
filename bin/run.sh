#!/bin/sh

/bin/sh -c "echo '0 * * * * TELEGRAM_TOKEN=$TELEGRAM_TOKEN /usr/local/bin/python /web/tasks.py' >> /etc/crontabs/root"
/bin/sh -c "echo '* * * * * root echo Im alive >> /var/log/cron.log 2>&1' >> /etc/crontabs/root"
/bin/sh -c "touch /var/log/cron.log && crond"
/bin/sh -c "alembic upgrade head"
/bin/sh -c "python admin.py"
