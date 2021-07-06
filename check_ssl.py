#!/usr/bin/python

import os
import ssl
import json
import yaml
from time import sleep, time
import socket
from datetime import datetime, date
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


try:
    filesource = os.environ['LIST']
except KeyError:
    print('Missing LIST environment variable, exiting.')
    exit(1)

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

def connect_to_influxdb():
    try:
        influxdb_host = os.environ['INFLUXDB-HOST']
    except:
        print('INFLUXDB-HOST environnement variable is not set, running without InfluxDB')
        return None
    else:
        if (influxdb_host != None and influxdb_host != ''):
            try:
                os.environ['INFLUXDB-TOKEN']
                os.environ['INFLUXDB-ORG']
                os.environ['INFLUXDB-BUCKET']
            except:
                print('INFLUXDB-HOST is defined please define INFLUX-TOKEN, INFLUX-ORG and INFLUX-BUCKET environnement variables.')
                exit(1)
        else:
            print('INFLUXDB-HOST environnement variable is empty, running without InfluxDB')
            return None
        if (influxdb_host != None and influxdb_host != ''):
            client = InfluxDBClient(url=influxdb_host, token=os.environ['INFLUXDB-TOKEN'])
            return client.write_api(write_options=SYNCHRONOUS)


def insert_to_influxdb(write_api, hostname, expiration, dns, delta, tags):
    new_delta = f'{delta}'.split()[0]
    sequence = [
        f'ssl_check,host={hostname} expiration="{expiration}",dns="{dns}",delta={new_delta}'
    ]
    if tags != []:
        sequence.append(f'tags,host={hostname} tags="{tags}"')
    while True:
        try:
            write_api.write(os.environ['INFLUXDB-BUCKET'], os.environ['INFLUXDB-ORG'], sequence)
        except:
            print('Waiting 10 seconds for InfluxDB to start...')
            sleep(10)
        else:
            break

def main():
    while 42:
        data = open_file()
        today = datetime.today()
        write_api = connect_to_influxdb()

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
                if write_api != None:
                    insert_to_influxdb(write_api, hostname, expiration, dns, delta, tags)
                else:
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