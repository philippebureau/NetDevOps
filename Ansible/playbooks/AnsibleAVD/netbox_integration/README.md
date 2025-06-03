# Netbox integration with AVD

## netbox_import_interfaces.yml

This playbook import interfaces from Netbox configured with the tag defined in the playbook var 'target_tag'

> note: use the tag slug, not the tag name.  Slug is the same as name but all lower case and spaces replaced with -

The playbook var 'template_file' needs to point to a copy of the file called 'network_ports.j2' in the templates folder in this directory

The output will be in a dedicated file defined in plabook var 'file_output'

The output will use AVD network_ports data model using a custom key 'netbox_import'

To merge with manually entered network_ports data, use a custom key for that too and merge the 2 arrays.

Example:

    # Network Ports model (Network centric)
    # using a custom key to merge later
    avd_network_ports:
    - switches: [ dc2-leaf1 ]
        switch_ports: [ Ethernet4 ]
        description: host dc2-host1 Et1
        mode: access
        vlans: 100
    - switches: [ dc2-leaf2 ]
        switch_ports: [ Ethernet4 ]
        description: host dc2-host1 Et2
        mode: access
        vlans: 100
    - switches:
        - dc2-leaf3
        switch_ports:
        - Ethernet4
        description: host dc2-host2 Et1
        mode: access
        vlans: 200
    - switches:
        - dc2-leaf4
        switch_ports:
        - Ethernet4
        description: host dc2-host2 Et2
        mode: access
        vlans: 200

    # Merge netbox import interfaces
    # See netbox_import.yml in the CONNECTED_ENDPOINTS folder
    network_ports: "{{avd_network_ports + netbox_import | default([])}}"
