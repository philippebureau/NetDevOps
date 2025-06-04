AVD Netbox interfaces importer
=========

A brief description of the role goes here.

Requirements
------------

arista.avd ansible collection
netbox.netbox ansible collection
pyavd python library

Role Variables
--------------

  netbox_url: Example: "https://oohv9917.cloud.netboxapp.com"
    
  netbox_token: Netbox API token
    
  target_tag: The tag you want to use on Netbox that will trigger this role.  Use the tag slug, not name.  Tag slugs are usually the same as the name but all lower case and spaces replaced with -.  Example: tag AVD_IMPORT slug is avd_import
  
  file_output: Dedicated file for network ports output in the group_vars structure.  Use absolute path or path relative to the playbook.  Example: "../inventory/DataCenter/group_vars/CONNECTED_ENDPOINTS/netbox_import.yml"


Dependencies
------------

None

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - name: Get interfaces from netbox
      hosts: localhost
      gather_facts: false
      roles:
         - philippebureau.avd_netbox_interfaces_importer
      vars:
        netbox_url: "https://oohv9917.cloud.netboxapp.com"
        netbox_token: "{{vault_netbox_token}}"
        target_tag: avd_import
        file_output: "../inventory/DataCenter/group_vars/CONNECTED_ENDPOINTS/netbox_import.yml"
        


License
-------

BSD

Author Information
------------------

Philippe Bureau
  - https://github.com/philippebureau
