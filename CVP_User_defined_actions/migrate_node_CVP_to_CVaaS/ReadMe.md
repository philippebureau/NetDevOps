# Migrate to CVaaS

This script will migrage the selected node to a CVaaS instance.

An onboarding token needs to be generated on CVaaS and defined in the argument in the action "manage arguments" tab on CVP.  Onboarding tokens are generic and can be used for multiple devices.  Please generate one that will be valid for the duration of the onbording.  To update the token in the YAML file, the user-defined action needs to be removed and re-added.

To validate if a token has expired, you can check here: https://jwt.io/

The node will start streaming telemetry to the CVaaS instance which will automatically add the node in the inventory and the undefined container.

See the TOI on how to create custom actions in CVP UI : https://www.arista.com/en/support/toi/cvp-2021-3-0/14901-ui-for-custom-action-scripts