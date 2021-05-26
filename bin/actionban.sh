#!/bin/bash
# Declare function
function actionban {
PYTHON_ARG="$1" python3 - <<END
import os
ip = os.environ['PYTHON_ARG']
import f2bsophosxg.libf2b
f2bsophosxg.libf2b.ban(ip)
END
}
# Call the function
actionban $1
