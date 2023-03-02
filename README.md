orion_ipam
=========

This collection provides a module "orion_ipam_record" that retrieves an IP address from Solarwinds Orion IPAM

Requirements
------------

orionsdk>=0.3.0
requests>=2.28.2,<3.0

Role Variables
--------------

None

Dependencies
------------

None

Example Playbook
----------------

This is an example of how to retrive and IP address

    ---
    - name: "Get IP Address from Orion"
      connection: ssh
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
        - name: "Get IP"
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

License
-------

The MIT License (MIT)

