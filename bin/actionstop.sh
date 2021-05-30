#!/bin/bash
# Declare function
function actionstop {
PYTHON_ARG="$1" python3 - <<END
import sys
import f2bsophosxg.libf2b
ret = f2bsophosxg.libf2b.stop()
sys.exit(ret)
END
}
# Call the function
actionstop $1
RET=$?
exit $RET
