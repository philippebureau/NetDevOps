## this playbook helps with provisionning nodes in the ACT topology

> node: only Ubuntu was tested 

## Requirements: 
- ansible-github_actions_runner role [here](https://github.com/MonolithProjects/ansible-github_actions_runner)

### instructions
1- Update the inventory to match your node type in ACT

2- Update group_vars/hosts.yml with values that match your ACT topology

3- Update host_vars/* for your lab needs
>>> note: The playbook looks in rc.local for 'ip link set et1 up' and replaces it with the conent of the rc_local_config key value for each node matching the host_vars/x file.

4- Run the playbook.
    
    ansible-playbook playbooks/Lab_hosts_config.yml -i inventory/inventory.yml