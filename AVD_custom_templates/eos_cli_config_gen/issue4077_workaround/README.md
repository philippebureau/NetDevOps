# instructions



see AVD doc :
[link](https://avd.sh/en/stable/roles/eos_cli_config_gen/docs/how-to/custom-templates.html#adding-the-custom-template-to-group-vars)

replace eos_cli_config_gen key "system" with "custom_system"

## example

```yaml
custom_templates:
  - system_ACL_issue4077.j2

custom_system:
  control_plane:
    ipv4_access_groups:
      - acl_name: ACL_TEST_COPP
        vrf: MGMT
      - acl_name: ACL_TEST_COPP
      - acl_name: ACL_TEST_COPP
        vrf: VRF3
```
