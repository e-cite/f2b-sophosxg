#!/bin/bash
# Declare function
function actionunban {
PYTHON_ARG="$1" python3 - <<END
import os
import sys
ip = os.environ['PYTHON_ARG']
import f2bsophosxg.libf2b
ret = f2bsophosxg.libf2b.unban(ip)
sys.exit(ret)
END
}
# Call the function
actionunban $1
RET=$?
exit $RET
