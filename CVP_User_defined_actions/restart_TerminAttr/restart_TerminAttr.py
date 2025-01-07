import json
from cvplibrary.auditlogger import alog
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue(GlobalVariableNames.SCRIPT_ARGS)

target = Device(ip)
cmdList = [ "enable" , "show hostname" ]
cmdResponse = target.runCmds(cmdList)
hostname = cmdResponse[1]['response']['hostname']

alog("restarting TerminAttr from script on %s" % (hostname))

target.runCmds(["enable", "configure", "daemon TerminAttr", "shutdown", "no shutdown"])
