import os
import time

from digitalocean import DigitalOceanClient

setup_commands = """
#cloud-config
packages:
  - curl
  - git
  - make
runcmd:
  - curl -L "https://github.com/docker/compose/releases/download/1.9.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  - chmod +x /usr/local/bin/docker-compose
  - git clone https://github.com/synnick/django-playground.git /opt/apps/django-playground
"""[1:-1] # remove \n at start and end


client = DigitalOceanClient(os.environ['DIGITALOCEAN_ACCESS_TOKEN'])
ssh_key = client.get_ssh_key_by_name('Emmanuel')
if ssh_key:
    droplet = client.create_droplet(**{
        "name": "testing",
        "region": "nyc3",
        "size": "512mb",
        "image": "docker",
        "ssh_keys": [ssh_key['id']],
        "backups": False,
        "ipv6": False,
        "user_data": setup_commands,
        "private_networking": None,
        "volumes": None,
        "tags": ["testing"],
    })
    print 'Droplet created'
