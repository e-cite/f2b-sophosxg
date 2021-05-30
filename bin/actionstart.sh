#!/bin/bash
# Declare function
function actionstart {
PYTHON_ARG="$1" python3 - <<END
import sys
import f2bsophosxg.libf2b
ret = f2bsophosxg.libf2b.start()
sys.exit(ret)
END
}
# Call the function
actionstart $1
RET=$?
exit $RET
