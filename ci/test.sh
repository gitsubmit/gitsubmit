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

# start a testing server on port 5555
python src/app.py -p 5555 &

TESTSERVERPID=$!
sleep 3 # let tornado warm up

cd test
# Run tests with an X virtual frame buffer
xvfb-run --server-args="-screen 0, 1920x1080x24" python -m robot.run --noncritical not_implemented .
kill $TESTSERVERPID
