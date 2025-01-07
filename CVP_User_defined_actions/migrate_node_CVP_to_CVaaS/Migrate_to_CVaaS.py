###
# Arguments needs to be set as follow
# DeviceID 
# TOKEN
# VRF
###

import json

# This script can be used to migrate nodes from CVP on-prem to CVaaS
# An onboarding token needs to be generated on CVaaS and defined in the argument in the YAML file

TOKEN = ctx.changeControl.args.get("TOKEN")
VRF = ctx.changeControl.args.get("VRF")

# Write an entry to CVP Log
ctx.alog("Migrating node to CVaaS")

# Migration
try:
    ctx.runDeviceCmds(["enable", \
      {"cmd": "copy terminal: file:/tmp/cv-onboarding-token", "input": TOKEN}, \
     "configure", \
     "daemon TerminAttr", \
     "exec /usr/bin/TerminAttr -cvaddr=apiserver.arista.io:443 -cvcompression=gzip -cvvrf=%s -disableaaa -taillogs -cvauth=token-secure,/tmp/cv-onboarding-token -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent" % (VRF), \
     "no shutdown"])
except:
    ctx.alog("Migration failed")
else:
    ctx.alog("Migration succeded")
