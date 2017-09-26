#!/usr/bin/python

#
# Author: Amir Mofasser <amir.mofasser@gmail.com>
#
# This is an Ansible module. Installs/Uninstall IBM Installation Manager
#

DOCUMENTATION = """
module: profile_nodeagent
version_added: "1.9.4"
short_description: Manage a WebSphere Application Server profile
description:
  - Manage a WebSphere Application Server profile
options:
  state:
    required: false
    choices: [ present, absent, purge ]
    default: "present"
    description:
      - The profile should be created (present), removed (absent) or removed and directory removed (purge)
  profile_name:
    required: true
    description:
      - Name of the profile
  wasdir:
    required: true
    description:
      - Path to installation folder of WAS
  profile_dir:
    required: false
    description:
      - Optional path to profile folder, will use wasdir/profiles if undefined
  cell_name:
    required: false
    description:
      - Cell Name
  host_name:
    required: false
    description:
      - Nodeagent host name
  password:
    required: false
    description:
      - Deployment manager password
  username:
    required: false
    description:
      - Deployment manager username
  dmgr_host:
    required: false
    description:
      - Deployment manager host name
  dmgr_port:
    required: false
    default: 8879
    description:
      - Deployment manager port
  federate:
    required: false
    choices: true, false
    description:
      - Wether to federate this node agent profile to a cell
  template_name:
    required: false
    default: managed
    description:
      - Template name to base this profile on. Templates are typically a directory in wasdir/profileTemplates
  admin_security:
    required: false
    default: true
    choices: [ 'true', 'false' ]
    description:
      - Wether to enable admin security or not (for development is it useful to disable)
author: "Amir Mofasser (@amofasser)"
"""

EXAMPLES = """
# Install:
profile_nodeagent: state=present wasdir=/usr/local/WebSphere profile_dir=/shared/WasProfiles profile_name=nodeagent cell_name=myNodeCell host_name=node.domain.com node_name=mycell-node1 username=wasadmin password=waspass dmgr_host=dmgr.domain.com dmgr_port=8879 federate=true template_name=managed admin_security='true'
# Uninstall
profile_nodeagent: state=purge wasdir=/usr/local/WebSphere profile_name=nodeagent
"""

import os
import subprocess
import platform
import datetime
import shutil

def isProvisioned(dest, profileName):
    """
    Runs manageprofiles.sh -listProfiles command nd stores the output in a dict
    :param dest: WAS installation dir
    :param profilesName: Profile Name
    :return: boolean
    """
    if not os.path.exists(dest):
        return False
    else:
        child = subprocess.Popen(
            ["{0}/bin/manageprofiles.sh -listProfiles".format(dest)],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()

        if profileName in stdout_value:
            return True
    return False

def main():

    # Read arguments
    module = AnsibleModule(
        argument_spec       = dict(
            state           = dict(default='present', choices=['present', 'absent','purge']),
            wasdir          = dict(required=True),
            profile_dir     = dict(required=False),
            profile_name    = dict(required=True),
            cell_name       = dict(required=False),
            host_name       = dict(required=False),
            node_name       = dict(required=False),
            username        = dict(required=False),
            password        = dict(required=False),
            dmgr_host       = dict(required=False),
            dmgr_port       = dict(required=False, default='8879'),
            federate        = dict(required=False, choices=BOOLEANS),
            admin_security  = dict(required=False, choices=BOOLEANS, default='true'),
            template_name   = dict(required=False, default='managed')
        )
    )

    state           = module.params['state']
    wasdir          = module.params['wasdir']
    profile_dir     = module.params['profile_dir']
    profile_name    = module.params['profile_name']
    cell_name       = module.params['cell_name']
    host_name       = module.params['host_name']
    node_name       = module.params['node_name']
    username        = module.params['username']
    password        = module.params['password']
    dmgr_host       = module.params['dmgr_host']
    dmgr_port       = module.params['dmgr_port']
    federate        = module.params['federate']
    admin_security  = module.params['admin_security']
    template_name   = module.params['template_name']


    # If was dir ends with a slash, remove the slash eg /opt/ becomes /opt
    if wasdir.endswith('/'):
        wasdir = wasdir[:-1]

    # Check if profile_dir has been defined. If not set it to the default
    if profile_dir is None:
        profile_dir = wasdir + '/profiles'

    if profile_dir.endswith('/'):
        profile_dir = profile_dir[:-1]

    # Check if paths are valid
    if not os.path.exists(wasdir):
        module.fail_json(msg=wasdir+" does not exists")

    if not os.path.exists(profile_dir):
        module.fail_json(msg=profile_dir+" does not exists")



    # Create a profile
    if state == 'present':
        if module.check_mode:
            module.exit_json(
                changed=False,
                msg="Profile {0} is to be created".format(profile_name)
            )

        if not isProvisioned(wasdir, profile_name):
            child = subprocess.Popen([
                "{0}/bin/manageprofiles.sh -create "
                "-profileName {1} "
                "-profilePath {7}/{1} "
                "-templatePath {0}/profileTemplates/{9} "
                "-cellName {2} "
                "-hostName {3} "
                "-nodeName {4} "
                "-enableAdminSecurity {8} "
                "-adminUserName {5} "
                "-adminPassword {6} ".format(wasdir, profile_name, cell_name, host_name, node_name, username, password, profile_dir, admin_security, template_name)],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                # Remove profile dir if creation fails so that it doesnt prevents us from retrying
                shutil.rmtree("{0}/{1}".format(profile_dir, profile_name), ignore_errors=False, onerror=None)

                module.fail_json(
                    msg="Profile {0} creation failed".format(profile_name),
                    stdout=stdout_value,
                    stderr=stderr_value
                )

            if federate:
                # Federate the node
                child = subprocess.Popen([
                    "{0}/bin/addNode.sh {1} {2} "
                    "-conntype SOAP "
                    "-username {3} "
                    "-password {4} "
                    "-profileName {5} ".format(wasdir, dmgr_host, dmgr_port, username, password, profile_name)],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg="Profile {0} federation failed".format(profile_name),
                        stdout=stdout_value,
                        stderr=stderr_value
                    )

            module.exit_json(
                changed=True,
                msg="Profile {0} created successfully",
                stdout=stdout_value
            )

        else:
            module.exit_json(
                changed=False,
                msg="Profile {0} already exists".format(profile_name)
            )

    # Remove a profile
    if state in ['absent','purge']:
        if module.check_mode:
            module.exit_json(
                changed=False,
                msg="Profile {0} is to be removed".format(profile_name)
            )

        if isProvisioned(wasdir, profile_name):

            child = subprocess.Popen([
                "{0}/bin/manageprofiles.sh -delete "
                "-profileName {1} ".format(wasdir, profile_name)],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                # manageprofiles.sh -delete will fail if the profile does not exist.
                # But creation of a profile with the same name will also fail if
                # the directory is not empty. So we better remove the dir forcefully.
                if not stdout_value.find("INSTCONFFAILED") < 0:
                    shutil.rmtree("{0}/{1}".format(profile_dir, profile_name), ignore_errors=False, onerror=None)
                else:
                    module.fail_json(
                        msg="Profile {0} removal failed".format(profile_name),
                        stdout=stdout_value,
                        stderr=stderr_value
                    )

            if state == 'purge':
                if os.path.exists(profile_dir+'/'+profile_name):
                    shutil.rmtree("{0}/{1}".format(profile_dir, profile_name), ignore_errors=False, onerror=None)

            module.exit_json(
                changed=True,
                msg="Profile {0} removed successfully".format(profile_name),
                stdout=stdout_value,
                stderr=stderr_value
            )

        else:
            if state == 'purge':
                if os.path.exists(profile_dir+'/'+profile_name):
                    shutil.rmtree("{0}/{1}".format(profile_dir, profile_name), ignore_errors=False, onerror=None)

                    module.exit_json(
                        changed=True,
                        msg="Profile {0} purged successfully".format(profile_name),
                    )
                else:
                    module.exit_json(
                        changed=False,
                        msg="Profile {0} does not exist".format(profile_name)
                    )
            else:
                module.exit_json(
                    changed=False,
                    msg="Profile {0} does not exist".format(profile_name)
                )

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
