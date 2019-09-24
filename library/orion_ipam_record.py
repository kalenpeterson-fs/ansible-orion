#!/usr/bin/python

# Copyright: (c) 2019, Kalen Peterson <kalen.peterson@siriuscom.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '0.2',
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
    new_ip_status:
        description:
            - The IPAM Record Status to set for the provisioned IP
            - "Used", "Available", "Reserved", "Transient", "Blocked"
        required: false
        default: "Used"
    new_ip_comment:
        description:
            - The IPAM Record Comment to set for the provisioned IP
        required: false
        default: "Updated by Ansible"
    ping_test:
        description:
            - Option to perform a ping test before returning the IP
        required: false
        default: true
    retry_limit:
        description:
            - Number of times to validate an IP from Orion before failing
        required: false
        default: 5

author:
    - Kalen Peterson (@kpeterson-sirius)
'''

EXAMPLES = '''
# Get the next available IP Address in 10.0.0.0/24
- name: Get Next IP
  orion_ipam_record:
    subnet: '10.0.0.0 /24'
    orion_server: 'orion.server.com'
    orion_username: 'orionapiuser'
    orion_password: 'orionapipass'

# Get the next available IP Address in 10.0.0.0/24, with optional args
- name: Get Next IP
  orion_ipam_record:
    subnet: '10.0.0.0 /24'
    orion_server: 'orion.server.com'
    orion_username: 'orionapiuser'
    orion_password: 'orionapipass'
    new_ip_status: 'Transient'
    new_ip_comment: 'Changed by Script'
    ping_test: false
    retry_limit: 1
'''

RETURN = '''
ip_address:
    description: The returned IP Address
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import os

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
        new_ip_status=dict(type='str', required=False, default='Used'),
        new_ip_comment=dict(type='str', required=False, default='Updated by Ansible'),
        ping_test=dict(type='bool', required=False, default=True),
        retry_limit=dict(type='int', required=False, default=5)
    )

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

    # Check for ORION
    if not HAS_ORION:
        module.fail_json(msg="orionsdk is required for this module. please install it")

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # Send Request for top {retry_limit} IP Addresses
    swis = SwisClient(module.params['orion_server'], module.params['orion_username'], module.params['orion_password'])
    try:
        results = swis.query("SELECT TOP {retry_limit} I.Status, I.IPAddress, I.DisplayName, Uri, I.Comments FROM IPAM.IPNode I WHERE Status=2 AND I.Subnet.DisplayName = @subnet", subnet=module.params['subnet'])
    except:
        module.fail_json(msg="Failed to query Orion. Check orion_server, orion_username, and orion_password {0}".format(str(e)), **result)


    # Find a Valid/Free IP from the request
    for i in range(module.params['retry_default']):

        # Check if there was a valid request
        if not results["results"][i]:
            continue

        # Perform a Ping Test
        if module.params['ping_test']:
            ping_response = os.system("ping -c 1 " + results["results"][i]['IPAddress'])
            if ping_response == 0:
                print("{ip_address} is Alive")
                continue
            else:
                print("{ip_address} is Not Alive")
                ip_address = results["results"][i]['IPAddress']
                uri = results["results"][i]['Uri']
                break
        else:
            ip_address = results["results"][i]['IPAddress']
            uri = results["results"][i]['Uri']

    # Did we get an OK IP Address?
    if ip_address:
        # Set the Status
        try:
            swis.update(uri, Status=module.params['new_ip_status'])
        except:
            module.fail_json(msg="Failed to update status {0}".format(str(e)), **result)

        # Set the Comments
        try:
            swis.update(uri, Comments=module.params['new_ip_comments'])
        except:
            module.fail_json(msg="Failed to update comment {0}".format(str(e)), **result)

        # Set SkipScan to False
        try:
            swis.update(uri, SkipScan=False)
        except:
            module.fail_json(msg="Failed to set SkipScan to False {0}".format(str(e)), **result)

        # Set the Module Result
        result['ip_address'] = ip_address
        result['changed'] = True
    else:
        module.fail_json(msg="Failed to find an unused IP Address", **result)

    # Exit Module
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
