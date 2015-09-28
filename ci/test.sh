#!/usr/bin/env bash
set -e # exit with non-zero exit codes immediately
if [ "$local_instance" = "yes" ]; then
    # this is on a server
    . ~/gitsubmitenv/bin/activate
else
    # This is probably being run locally by shawkins
    . /virtualenvs/gitsubmit_env/bin/activate
fi
pip install -r requirements.txt

cd src
# start a testing server on port 5555
/virtualenvs/gitsubmit_env/bin/gunicorn --access-logfile /srv/logs/staging_access.log -w 1 -b :5555 app:app &

TESTSERVERPID=$!
echo $TESTSERVERPID > ../staging_pid
sleep 3 # let gunicorn warm up

cd ../test
# Run tests with an X virtual frame buffer
xvfb-run --server-args="-screen 0, 1920x1080x24" python -m robot.run --noncritical not_implemented .
kill $TESTSERVERPID
