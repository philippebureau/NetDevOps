import json
from cvplibrary.auditlogger import alog
from cvplibrary import Device, CVPGlobalVariables, GlobalVariableNames
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP)
scriptArgs = CVPGlobalVariables.getValue(GlobalVariableNames.SCRIPT_ARGS)

#You can use this script to check Aboot version for Field Notice 0044
#https://www.arista.com/en/support/advisories-notices/fieldnotices/8756-field-notice-44
#It can log in CVP audit logger in the Change Control and/or to a text file.
#Use the YAML file to control log action

target = Device(ip)
cmdList = [ "enable" , "show hostname" , "show version detail" ]
cmdResponse = target.runCmds(cmdList)
hostname = cmdResponse[1]['response']['hostname']
norcal = cmdResponse[2]['response']['details']['components'][int('0')]['version']
aboot_version = norcal.split("-")[2]
major_version = int(aboot_version.split(".")[0] + aboot_version.split(".")[1])
minor_version = int(aboot_version.split(".")[2])

def gen_log_to_alog(major_version, minor_version, hostname, aboot_version):
  if major_version == 40 and minor_version < 7:
    alog("Aboot on %s is version %s needs to be patched" % (hostname, aboot_version))
  elif major_version == 41 and minor_version < 1:
    alog("Aboot on %s is version %s needs to be patched" % (hostname, aboot_version))
  elif major_version == 60 and minor_version < 9:
    alog("Aboot on %s is version %s needs to be patched" % (hostname, aboot_version))
  elif major_version == 61 and minor_version < 7:
    alog("Aboot on %s is version %s needs to be patched" % (hostname, aboot_version))
  else:
    alog("Aboot on %s is fine" % (hostname,))
  return

def gen_log_file(major_version, minor_version, hostname, aboot_version):
  outF = scriptArgs[ "outfile" ]
  output = open(outF, "a")
  if major_version == 40 and minor_version < 7:
	  output.write('Aboot on %s is version %s needs to be patched\n' % (hostname, aboot_version))
  elif major_version == 41 and minor_version < 1:
	  output.write('Aboot on %s is version %s needs to be patched\n' % (hostname, aboot_version))
  elif major_version == 60 and minor_version < 9:
	  output.write('Aboot on %s is version %s needs to be patched\n' % (hostname, aboot_version))
  elif major_version == 61 and minor_version < 7:
	  output.write('Aboot on %s is version %s needs to be patched\n' % (hostname, aboot_version))
  else:
	  output.write('Aboot on %s is fine\n'% (hostname)) 
  output.close()
  return

def main():
  writetoalog = scriptArgs[ "alog" ]
  writetofile = scriptArgs[ "file" ]
  if writetoalog == 'YES':
    gen_log_to_alog(major_version, minor_version, hostname, aboot_version)
  if writetofile == 'YES':
    gen_log_file(major_version, minor_version, hostname, aboot_version)


if __name__ == '__main__':
   main()