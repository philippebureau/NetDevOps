import json
from cvplibrary.auditlogger import alog
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)

alog("Running 'Clear /var/log/' from script")

target = Device(ip)

target.runCmds(["bash timeout 5 sudo rm /var/core/core.*"])
