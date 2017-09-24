#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['beta'],
    'supported_by': 'CODE/ team'
}

DOCUMENTATION = '''
---
module: dir_ops

short_description: easy way to prune directory under a path based on size.

version_added: "1.0"

description:
    - "There is no standard way in ansible to estimate the conent size of a directory.
       This module help to calculate the size and delete them"

options:
    path:
        description:
            - The path where the directories need to be checked
        required: true
    size:
        description:
            - the size in mb or gb above which we should prune
        required: true

author:
    - Kiran Ramachandra
'''

EXAMPLES = '''
$cat playbook_ops.yml
- name: test my new module
  connection: local
  hosts: localhost
  tasks:
  - name: Run directory ops
    dir_ops:
      path: /tmp/test/
      size: 15000000  # this is 15MB
    register: testout
  - name: dump test output
    debug:
      msg: '{{ testout }}'

execute python : 
$python modules/commands/dir_ops.py /tmp/args.jsonython modules/commands/dir_ops.py /tmp/args.json

$ cat /tmp/args.json
{
    "ANSIBLE_MODULE_ARGS": {
        "path": "/home/kiran",
        "size": 1000000
    }
}

'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''
import os
import shutil
from ansible.module_utils.basic import AnsibleModule

def dir_content_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            #link files are not part of size
            if not os.path.islink(os.path.join(root,name)):
                #print os.path.join(root,name)," " ,os.stat(os.path.join(root,name)).st_size
                total += os.stat(os.path.join(root,name)).st_size
        for name in dirs:
            #print name , " is a dir " , os.stat(os.path.join(root,name)).st_size
            total += os.stat(os.path.join(root,name)).st_size
    # add size of current working directory
    total += os.stat(path).st_size
    return total


def run_module():

    module_args = dict(
        path=dict(type='str', required=True),
        size=dict(type='int', required=True)
    )

    result = dict(
        changed=False,
        original_size='',
        changed_size=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if in check mode, return for now.
    # eventually check mode should be supported
    if module.check_mode:
        return result
    path = module.params['path']
    # get current size of the given path
    result['original_message'] = module.params['path']
    changed = 0
    msg = ""
    for item in os.listdir(path):
        size = dir_content_size(os.path.join(path, item))
        print "compare ", os.path.join(path, item), " of size " , size, " with ", module.params['size']
        if int(size) > module.params['size']:
            msg += "Removing "+ os.path.join(path, item) +"\n"
            shutil.rmtree(os.path.join(path, item))
            changed = 1

    result['message'] = "Deleted all items above specified size from the path" + msg

    if changed == 1:
        result['changed'] = True


    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()

