# CleanVarCore action

This script will delete all files from /var/core/

It can be used to fix switches with the bellow error message:

    Warning: the following filesystems have less than 10% free space left:
     /var/core                    0% (   0 bytes) Available

To make this script available in CVP Change Controls:

* log into CVP shell as root
* copy the script and YAML file to a local folder 
    * you can copy directly from github using `wget https://raw.githubusercontent.com/philippebureau/CVP_User-defined_actions_public/main/CleanVarCore/CleanVarCore.py https://raw.githubusercontent.com/philippebureau/CVP_User-defined_actions_public/main/CleanVarCore/cfg_CleanVarCore.yaml`
* install using script-util 
    * ex : `/cvpi/tools/script-util upload -path CleanVarCore.py -config cfg_CleanVarCore.yaml`
* validate with command `/cvpi/tools/script-util list`