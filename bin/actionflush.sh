#!/bin/bash
# Declare function
function actionflush {
PYTHON_ARG="$1" python3 - <<END
import sys
import f2bsophosxg.libf2b
ret = f2bsophosxg.libf2b.flush()
sys.exit(ret)
END
}
# Call the function
actionflush $1
RET=$?
exit $RET
