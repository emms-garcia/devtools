import requests
import time


def merge_dicts(a, b):
    return dict(a.items() + b.items())


class Droplet(object):
    DELETE_POLLING = 5

    def __init__(self, client, **kwargs):
        self.client = client
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def delete(self):
        while self.status == 'new':
            time.sleep(self.DELETE_POLLING)
            self.sync()

        response = self.client._delete(
            '{}/droplets/{}'.format(self.client.BASE_API_URL, self.id)
        )
        if not response.ok:
            raise Exception(
                'Droplet delete failed. Response: {}'.format(response.content)
            )

    def sync(self):
        response = self.client._get(
            '{}/droplets/{}'.format(self.client.BASE_API_URL, self.id)
        )
        if not response.ok:
            raise Exception(
                'Droplet sync failed. Response: {}'.format(response.content)
            )

        droplet = response.json().get('droplet', {})
        for key, value in droplet.iteritems():
            setattr(self, key, value)


class DigitalOceanClient(object):
    BASE_API_URL = 'https://api.digitalocean.com/v2'

    def __init__(self, access_token):
        self.headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
        }

    def _delete(self, *args, **kwargs):
        kwargs['headers'] = merge_dicts(
            self.headers, kwargs.get('headers', {})
        )
        return requests.delete(*args, **kwargs)

    def _get(self, *args, **kwargs):
        kwargs['headers'] = merge_dicts(
            self.headers, kwargs.get('headers', {})
        )
        return requests.get(*args, **kwargs)

    def _post(self, *args, **kwargs):
        kwargs['headers'] = merge_dicts(
            self.headers, kwargs.get('headers', {})
        )
        return requests.post(*args, **kwargs)

    def create_droplet(self, **kwargs):
        response = self._post('{}/droplets'.format(
            self.BASE_API_URL), json=kwargs
        )
        if response.ok:
            droplet = response.json().get('droplet', {})
            return Droplet(self, **droplet)

        raise Exception(
            'Droplet create failed. Response: {}'.format(response.content)
        )

    def get_droplets(self):
        response = self._get('{}/droplets'.format(self.BASE_API_URL))
        return [
            Droplet(self, **droplet)
            for droplet in response.json().get('droplets', [])
        ]

    def get_ssh_keys(self):
        response = self._get('{}/account/keys'.format(self.BASE_API_URL))
        return response.json().get('ssh_keys', [])

    def get_ssh_key_by_name(self, name):
        for ssh_key in self.get_ssh_keys():
            if ssh_key['name'] == name:
                return ssh_key
        return None

    def ping(self):
        url = '{}/account'.format(self.BASE_API_URL)
        return self._get(url).ok
