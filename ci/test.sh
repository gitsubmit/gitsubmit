#!/usr/bin/env bash

# in case they weren't stopped last time
docker stop gitotestname
docker rm gitotestname
docker stop mongotestname
docker rm mongotestname

set -e # exit with non-zero exit codes immediately
if [ "$local_instance" = "yes" ]; then
    # this is not on a server
    . ~/gitsubmitenv/bin/activate
else
    # This is probably being run locally by shawkins
    . /virtualenvs/gitsubmit_env/bin/activate
fi
pip install -r requirements.txt

# Start up a docker instance for the gitolite repo
docker run --name gitotestname -p 3022:22 -e SSH_KEY="$(cat /home/git/.ssh/id_rsa.pub)" elsdoerfer/gitolite &
docker run --name mongotestname -p 27117:27017 -e AUTH=no tutum/mongodb &

sleep 10 # let docker warm up


# Get a copy of the faked gitolite repo
# note: see ~git/.ssh/config for info on this; contents below
# Host gitolite_test_git
# StrictHostKeyChecking no
# User git
# Hostname api.gitsubmit.com
# Port 3022

yes | rm -r gitolite-admin || true
git clone gitolite_test_git:gitolite-admin
GL_PATH=$(readlink -f gitolite-admin/)
TEST_PATH=$(pwd)


# do the setup we need for pyolite to work
cd $GL_PATH
echo 'include     "repos/**/*.conf"' >> conf/gitolite.conf
echo 'include     "repos/*.conf"' >> conf/gitolite.conf
git add conf
git commit -m "initial setup for pyolite"
git push


# get back to where we were
cd $TEST_PATH

# shove some data in there
python ci/fill_db_with_fake_data.py -p 27117 -pyo $GL_PATH

cd src
# start a testing server on port 5555
/virtualenvs/gitsubmit_env/bin/gunicorn --access-logfile /srv/logs/staging_access.log -w 1 -b :5555 "app:configured_main('$GL_PATH', 27117)" &

TESTSERVERPID=$!
echo $TESTSERVERPID > ../staging_pid
sleep 3 # let gunicorn warm up

cd ../test
# Run tests with an X virtual frame buffer
export PYTHONPATH=$(readlink -f libraries):$(readlink -f resources):$PYTHONPATH
xvfb-run --server-args="-screen 0, 1920x1080x24" python -m robot.run --noncritical not_implemented .
kill $TESTSERVERPID

docker stop gitotestname
docker rm gitotestname
docker stop mongotestname
docker rm mongotestname

cd ..
rm bogus_key_*
