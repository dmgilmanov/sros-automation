import os
import yaml
import shutil
from netmiko import ConnectHandler, FileTransfer
from jinja2 import Environment, FileSystemLoader

def help_print():
    print("""
    Script usage:

    nuage-sros-config <action> <deployment>

      <action>          Requested action [generate|upload|reboot]
      <deployment>      Deployment directory name
    """)

def config_generate(deployment='default'):
    with open('deployments/' + deployment + '/common.yml') as f:
        common = yaml.load(f,Loader=yaml.FullLoader)
    with open('deployments/' + deployment + '/nodes.yml') as f:
        nodes = yaml.load(f,Loader=yaml.FullLoader)
    shutil.rmtree('output/' + deployment,ignore_errors=True)
    os.mkdir('output/' + deployment)
    environment = Environment(loader=FileSystemLoader('.'))
    for node in nodes.keys():
        node_path = 'output/' + deployment + '/' + node
        os.mkdir(node_path)
        template_bof = environment.get_template('templates/' + nodes[node]['node_type'] + '/bof.j2')
        template_config = environment.get_template('templates/' + nodes[node]['node_type'] + '/config.j2')
        print('Generating configuration files for {}'.format(node))
        with open(node_path + '/bof.cfg','w') as f:
            f.write(template_bof.render(common=common,node=nodes[node]))
        with open(node_path + '/config.cfg','w') as f:
            f.write(template_config.render(common=common,node=nodes[node]))

def config_upload(deployment='default'):
    with open('deployments/' + deployment + '/nodes.yml') as f:
        nodes = yaml.load(f,Loader=yaml.FullLoader)
    for node in nodes.keys():
        node_path = 'output/' + deployment + '/' + node
        ip_addr = nodes[node]['mgmt_ip']
        if 'vsc' in nodes[node]['node_type']:
            file_system = 'cf1:'
        else:
            file_system = 'cf3:'
        print('Pushing configuration files to {}'.format(node))
        with ConnectHandler(host=ip_addr,port='34002',username='admin',password='admin',device_type='nokia_sros') as device:
            with FileTransfer(device,source_file=node_path + '/bof.cfg', dest_file='bof.cfg',file_system=file_system,direction='put') as scp_transfer:
                scp_transfer.transfer_file()
            with FileTransfer(device,source_file=node_path + '/config.cfg', dest_file='config.cfg',file_system=file_system,direction='put') as scp_transfer:
                scp_transfer.transfer_file()

def node_reboot(deployment='default'):
    with open('deployments/' + deployment + '/nodes.yml') as f:
        nodes = yaml.load(f,Loader=yaml.FullLoader)
    for node in nodes.keys():
        ip_addr = nodes[node]['mgmt_ip']
        print('Rebooting {}'.format(node))
        with ConnectHandler(host=ip_addr,port='34002',username='admin',password='admin',device_type='nokia_sros') as device:
            device.send_command_timing('admin reboot now')

