#!/bin/bash

DIR=`dirname $0`
BOUNCER=${DIR}/../kubectl/bounce_erizo.sh

cd ${DIR}
${DIR}/erizomon.py
rc=$?
if [ $rc -gt 0 ]; then
    $BOUNCER
fi
exit $rc
