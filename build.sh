#!/bin/bash --verbose
rm -rf /psikon/python/envs/psistatsrd
virtualenv --system-site-packages /psikon/python/envs/psistatsrd
source /psikon/python/envs/psistatsrd/bin/activate
pip install -r $WORKSPACE/requirements.txt
pip install pylint

PYTHONPATH=$WORKSPACE:$PYTHONPATH

pylint -f parseable $WORKSPACE/ | tee pylint.out
/usr/bin/sloccount --duplicates --wide --details $WORKSPACE > sloccount.sc

cd $WORKSPACE
/psikon/sonar-runner/bin/sonar-runner
