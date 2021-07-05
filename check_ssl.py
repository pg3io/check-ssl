#!/usr/bin/python

import os
import ssl
import json
from time import sleep
from urllib.request import socket
from datetime import datetime, date
import yaml

filesource = os.environ['LIST']

def open_file():
    with open(filesource, 'r') as stream:
        try:
            file = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return file

def date_converter(o):
    if isinstance(o, datetime):
        return o.__str__()

def json_format(url, expiration, dns, delta, tags):
    data = {}

    data['url'] = url
    data['expiration'] = expiration
    data['dns'] = dns
    data['delta'] = delta.days
    if tags != []:
        data['tags'] = tags
    data = json.dumps(data, default=date_converter)

    print(data)

def format_url(base_url):
    new_url = base_url.replace('https://', '')
    if new_url.find('/') != -1:
        index = new_url.find('/')
        new_url = new_url[0:index]

    return new_url

def main():
    while 42:
        data = open_file()
        today = datetime.today()

        for url in data['website']:
            if url['ssl'] == True:
                base_url = url['url']
                port = '443'
                hostname = format_url(base_url)
                context = ssl.create_default_context()

                with socket.create_connection((hostname, port)) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        data = ssock.getpeercert()

                expiration = datetime.utcfromtimestamp(ssl.cert_time_to_seconds(data['notAfter']))
                delta = expiration - today
                dns = str(data['subjectAltName'])
                dns = dns.replace('(', '').replace(')', '').replace("'", '').replace('DNS', '').replace(' ', '')
                dns = dns[1:]
                dns = dns.split(',,')

                try:
                    tags = url['tags']
                except:
                    tags = []

                json_format(hostname, expiration, dns, delta, tags)

        try:
            data['ssl_delay']
        except:
            sleep(3600)
        else:
            sleep(int(data['ssl_delay']))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(1)