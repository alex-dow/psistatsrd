#!/bin/bash

WORKSPACE=/psikon/.jenkins/jobs/psistatsrd/workspace

PYTHONPATH=$WORKSPACE:$PYTHONPATH pylint $1 $2 $3 $4 $5 $6 $7
