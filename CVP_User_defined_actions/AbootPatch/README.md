# AbootPatch action

This script will install the Aboot patch for Field Notice 044

The image can be downloaded from any server using https.  File source is defined in the YAML file argument "extension_URL"

If using CVP as source for the patch file, it requires that CVP has an image bundle containing that Aboot patch file in it

If the installation is done over the none default VRF, change the VRF argument in the YAML config file

you need to define the name of the RPM file in the YAML file argument "extention"


To make this script available in CVP Change Controls:

* log into CVP shell as root
  * copy the script and YAML file to a local folder 
      * you can copy directly from github using `wget https://raw.githubusercontent.com/philippebureau/CVP_User-defined_actions_public/main/AbootPatch/AbootPatch.py https://raw.githubusercontent.com/philippebureau/CVP_User-defined_actions_public/main/AbootPatch/cfg_AbootPatch.yaml`
      * edit cfg_AbootPatch.yaml file arguments to match your environment
      * install using script-util 
        * ex : `/cvpi/tools/script-utils upload -path AbootPatch.py -config cfg_AbootPatch.yaml`
      * validate with command `/cvpi/tools/script-util list`

