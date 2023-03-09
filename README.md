orion_ipam
=========

This collection provides a module "orion_ipam_record" that retrieves an IP address from Solarwinds Orion IPAM.

**NOTE**

This module is not idempotent. A new IP address will be returned for each playbook run. You are responsible for reclaiming IP Addresses from Orion.

Requirements
------------

The follwing python packages are required:
```
orionsdk>=0.3.0
requests>=2.28.2,<3.0
ping3>=4.04,<5.0
```

When running in an Ansible Execution Environment, ping must be enabled on the host with the following command.

See the following KB for more info on enableing ICMP packets from non-root users: https://access.redhat.com/solutions/6859851

```
sysctl -w "net.ipv4.ping_group_range=0 2000000" >> /etc/sysctl.conf
```

Role Variables
--------------

None, this collection only contains a module

Dependencies
------------
         
None, this collection only contains a module

Example Playbook
----------------

This is an example of how to reserve an unused IP address in Orion IPAM and use it.

**NOTE**: This is not idempotent. Each playbook run will reserve and return a new IP Address.

```
---
- name: "Get IP Address from Orion"
  gather_facts: false
  hosts: localhost
  vars_prompt:
    - name: subnet
      private: no
    - name: orion_server
      private: no
    - name: orion_username
      private: no
    - name: orion_password
  tasks:

    - name: "Get next unused IP in this subnet"
      orion_ipam_record:
        subnet: "{{ subnet }}"
        orion_server: "{{ orion_server }}"
        orion_username: "{{ orion_username }}"
        orion_password: "{{ orion_password }}"
      register: orion_ipam_result
      become: true
      delegate_to: localhost

    - name: "Print IP"
      debug:
        msg: "{{ orion_ipam_result.ip_address }}"
```

License
-------

The MIT License (MIT)

