# README
A set of Ansible modules that lets you manage IBM packages

## Module Summary
| Module | Description |
|:-------|:------------|
| ibmim_installer.py | Installs and uninstalls IBM Installation Manager. |
| ibmim.py | Manage IBM Installation Manager packages. Currently supports Install/Uninstall and Update packages. |
| profile_dmgr.py | Creates or removes a WebSphere Application Server Deployment Manager profile. Requires a Network Deployment installation. |
| profile_nodeagent.py |Creates or removes a WebSphere Application Server Node Agent profile. Requires a Network Deployment installation. |
| profile_liberty.py | Creates or removes a Liberty Profile server runtime |
| server.py | Start or stops a WebSphere Application Server |
| liberty_server.py | Start or stops a Liberty Profile server |

## Modules

### ibmim_installer.py
This module installs or uninstalls IBM Installation Manager.

#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present, absent | present=install, absent=uninstall |
| src | false | N/A | N/A | Path to installation files for Installation Manager |
| dest | false | /opt/IBM/InstallationManager | N/A | Path to desired installation directory of Installation Manager |
| logdir | false | N/A | /tmp | Directory to save installation log file |

#### Example
```yaml
- name: Install:
  ibmim_installer:
    state: present
    src: /some/dir/install/
    logdir: /tmp/im_install.log

- name: Uninstall
  ibmim_installer:
    state: absent
    dest: /opt/IBM/InstallationManager
```

### ibmim.py
This module installs, uninstalls or updates IBM packages from local or remote repositories

#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | false | present | present, absent | present=install,absent=uninstall or update |
| ibmim | false | /opt/IBM/InstallationManager | N/A | Path to installation directory of Installation Manager |
| dest | false | N/A | N/A | Path to destination installation directory |
| im_shared | false | N/A | N/A | Path to Installation Manager shared resources folder |
| repo | false | N/A | N/A | Comma separated list of URLs or paths to installation repositories used by Installation Manager |
| id | true | N/A | N/A | ID of the package which you want to install |
| repositories | false | N/A | N/A | Comma separated list of repositories to use. May be a path, URL or both |
| properties | false | N/A | N/A | Comma separated list of properties needed for package installation. In the format key1=value,key2=value |
| install_fixes | false | none | N/A | Install fixes if available in the repositories |
| connect_passport_advantage | false | N/A | N/A | Append the PassportAdvantage repository to the repository list |

#### Example
```yaml
- name: Install WebSphere Application Server Liberty v8.5
  ibmim:
    id: com.ibm.websphere.liberty.BASE.v85
    repositories: /var/data/was

- name: Uninstall WebSphere Application Server Liberty v8.5
  ibmim:
    id: com.ibm.websphere.liberty.BASE.v85
    state: absent

- name: Update all packages
  ibmim:
    id: null
    state: update
    repositories: /var/data/was
```

### profile_dmgr.py
This module creates or removes a WebSphere Application Server Deployment Manager profile. Requires a Network Deployment installation.

#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | true | present | present,absent | present=create,absent=remove |
| wasdir | true | N/A | N/A | Path to installation location of WAS |
| profile_name | true | N/A | N/A | Name of the profile |
| cell_name | true | N/A | N/A | Name of the cell |
| host_name | true | N/A | N/A | Host Name |
| node_name | true | N/A | N/A | Node name of this profile |
| username | true | N/A | N/A | Administrative user name |
| password | true | N/A | N/A | Administrative user password |

#### Example
```yaml
- name: Create
  profile_dmgr:
    state: present
    wasdir: /usr/local/WebSphere/AppServer/
    profile_name: dmgr
    cell_name: devCell
    host_name: localhost
    node_name: devcell-dmgr
    username: admin
    password: allyourbasearebelongtous

- name: Remove
  profile_dmgr:
    state: absent
    wasdir: /usr/local/WebSphere/AppServer/
    profile_name: dmgr
```

### profile_nodeagent.py
This module creates or removes a WebSphere Application Server Node Agent profile. Requires a Network Deployment installation.
Note wasdir and profile_dir can end with or without a slash

#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | true | present | present,absent,purge | present=create,absent=remove,purge=remove and delete profile dir |
| wasdir | true | N/A | N/A | Path to installation location of WAS |
| profile_name | true | N/A | N/A | Name of the profile |
| profile_dir | false | wasdir/profiles | N/A | Optional path to profile folder, will use wasdir/profiles if undefined. Useful if your WAS dir is on shared storage and your profile is local |
| cell_name | true | N/A | N/A | Name of the cell |
| host_name | true | N/A | N/A | Host Name |
| node_name | true | N/A | N/A | Node name of this profile |
| username | true | N/A | N/A | Administrative user name of the deployment manager |
| password | true | N/A | N/A | Administrative user password of the deployment manager |
| dmgr_host | true | N/A | N/A | Host name of the Deployment Manager |
| dmgr_port | true | N/A | N/A | SOAP port number of the Deployment Manager |
| federate | false | N/A | N/A | Wether the node should be federated to a cell. If true, cell name cannot be the same as the cell name of the deployment manager. |
| admin_security | false | true | true, false | Wether admin security should be enabled or disabled (disabled is useful for early dev environments) |
| template_name | false | managed | N/A | template to be use for profiles |

#### Example
```yaml
- name: Create
  profile_nodeagent:
    state: 					present
    wasdir: 				/usr/local/WebSphere/AppServer
    profile_dir: 		/usr/local/WebSphereProfiles/
    profile_name: 	nodeagent
    cell_name: 			devCellTmp
    host_name: 			localhost
    node_name: 			devcell-node1
    username: 			admin
    password: 			allyourbasearebelongtous
    dmgr_host: 			localhost
    dmgr_port: 			8879
    federate: 			'true'
    template_name:  managed
    admin_security: 'true'

- name: Remove
  profile_nodeagent:
    state: 	absent
    wasdir: /usr/local/WebSphere/AppServer/
    name:		nodeagent

- name: Purge
  profile_nodeagent:
    state: 				purge
    wasdir: 			/usr/local/WebSphere/AppServer/
    profile_dir: 	/usr/local/WebSphereProfiles
    name: 				nodeagent
```

### server.py
This module start or stops a WebSphere Application Server

#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | true | started | started, stopped | N/A |
| name | true | N/A | N/A | Name of the app server |
| wasdir | true | N/A | N/A | Path to binary files of the application server |
| username | true | N/A | N/A | Administrative user name |
| password | true | N/A | N/A | Administrative user password |

#### Example
```yaml
- name: Start
  server:
    state: started
    wasdir: /usr/local/WebSphere/AppServer/
    name: my-server-01

- name: Stop
  server:
    state: stopped
    wasdir: /usr/local/WebSphere/AppServer/
    name: my-server-01
```

### liberty_server.py
This module start or stops a Liberty Profile server

#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | true | started | started, stopped | N/A |
| name | true | N/A | N/A | Name of the app server |
| libertydir | true | N/A | N/A | Path to binary files of the application server |

#### Example
```yaml
- name: Start
  liberty_server:
    state: started
    libertydir: /usr/local/WebSphere/Liberty/
    name: my-server-01

- name: Stop
  liberty_server:
    state: stopped
    libertydir: /usr/local/WebSphere/Liberty/
    name: my-server-01
```

### profile_liberty.py
This module creates or removes a Liberty Profile server runtime

#### Options
| Parameter | Required | Default | Choices | Comments |
|:---------|:--------|:---------|:---------|:---------|
| state | true | present | present,absent | present=create,absent=remove |
| libertydir | true | N/A | N/A | Path to install location of Liberty Profile binaries |
| name | true | N/A | N/A | Name of the server which is to be created/removed |

#### Example
```yaml
- name: Create
  profile_liberty:
    state: present
    libertydir: /usr/local/WebSphere/Liberty/
    name: server01

- name: Remove
  profile_liberty:
    state: absent
    libertydir: /usr/local/WebSphere/Liberty/
    name: server01
```
