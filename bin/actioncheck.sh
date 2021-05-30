#!/bin/bash
# Declare function
function actioncheck {
PYTHON_ARG="$1" python3 - <<END
import sys
import f2bsophosxg.libf2b
ret = f2bsophosxg.libf2b.check()
sys.exit(ret)
END
}
# Call the function
actioncheck $1
RET=$?
exit $RET
