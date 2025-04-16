from typing import List, Dict

from cloudvision.cvlib import ActionFailed

server = ctx.action.args.get("server")
path = ctx.action.args.get("path")
file_name = ctx.action.args.get("file_name")
vrf = ctx.action.args.get("vrf")
imageUrl = f"http://{server}{path}{file_name}"

ctx.info(f"Downloading {file_name} from {imageUrl}")
cmds = [
    "enable",
    f"cli vrf {vrf}",
    f"bash timeout 30 wget {imageUrl} -O /persist/secure/ssl/certs/{file_name}"
]
cmdResponses: List[Dict] = ctx.runDeviceCmds(cmds)
# Iterate through the list of responses for the commands, and if an error occurred in
# any of the commands, raise an exception
# Only consider the first error that is encountered as following commands require previous ones to succeed
errs = [resp.get('error') for resp in cmdResponses if resp.get('error')]
if errs:
    raise ActionFailed(f"File download failed with: {errs[0]}")
ctx.info("File download completed successfully")