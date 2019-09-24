#!/usr/bin/python

# Copyright: (c) 2019, Kalen Peterson <kalen.peterson@siriuscom.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: orion_ipam_record

short_description: Manage Solarwinds Orion IPAM Records

version_added: "2.8"

description:
    - "This module currently only supported requesting new IP Addresses in a given subnet"

options:
    subnet:
        description:
            - This is the subnet to request an address from
        required: true
    orion_server:
        description:
            - The Orion Server's hostname
        required: true
    orion_username:
        description:
            - The Orion Server's username
        required: true
    orion_password:
        description:
            - The Orion Server's password
        required: true

author:
    - Kalen Peterson (@kpeterson-sirius)
'''

EXAMPLES = '''
# Get the next available IP Address in 10.0.0.0/24
- name: Get Next IP
  orion_imap_record:
    subnet: '10.0.0.0/24'
    orion_server: 'orion.server.com'
    orion_username: 'orionapiuser'
    orion_password: 'orionapipass'

'''

RETURN = '''
ip_address:
    description: The returned IP Address
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule

import re
import requests
import sys
import json

try:
    from orionsdk import SwisClient
    requests.packages.urllib3.disable_warnings()
    HAS_ORION = True
except:
    HAS_ORION = False

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        subnet=dict(type='str', required=True),
        orion_server=dict(type='str', required=True),
        orion_username=dict(type='str', required=True),
        orion_password=dict(type='str', required=True, no_log=True),
    )

    # Check for ORION
    if not HAS_ORION:
        module.fail_json(msg="orionsdk is required for this module. pleae install it")

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        ip_address=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # Send Request
    swis = SwisClient(module.params['orion_server'], module.params['orion_username'], module.params['orion_password'])
    try:
        results = swis.query("SELECT TOP 1 I.Status, I.IPAddress, I.DisplayName, Uri, I.Comments FROM IPAM.IPNode I WHERE Status=2 AND I.Subnet.DisplayName = @subnet", subnet=module.params['subnet'])
    except:
        module.fail_json(msg="Failed to query Orion. Check orion_server, orion_username, and orion_password {0}".format(str(e)))

    #Check Request
    if results["results"][0]:
        result['ip_address'] = results["results"][0]['IPAddress']
        uri = results["results"][0]['Uri']
    else:
        module.fail_json(msg='Failed to find an available IP address')

    try:
        swis.update(uri, Status="Used")
    except:
        module.fail_json(msg="Failed to update status {0}".format(str(e)))

    try:
        swis.update(uri, Comments="Updated by Ansible")
    except:
        module.fail_json(msg="Failed to update comment {0}".format(str(e)))      

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    #if module.params['new']:
    #    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    #if module.params['name'] == 'fail me':
    #    module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
