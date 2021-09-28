#!/usr/bin/python

import os
import ssl
import json
import yaml
from time import sleep, time
import socket
from datetime import datetime, timedelta
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


def insert_to_influxdb(write_api, influxdb_connected, hostname, expiration, dns, delta, tags):
    new_delta = delta.days
    sequence = [
        f'ssl_check,host={hostname} expiration="{expiration}",dns="{dns}",delta={new_delta}'
    ]
    if tags != []:
        sequence.append(f'tags,host={hostname} tags="{tags}"')
    while True:
        try:
            write_api.write(os.environ['INFLUXDB-BUCKET'], os.environ['INFLUXDB-ORG'], sequence)
        except Exception as e:
            print('Waiting 10 seconds for InfluxDB to start...')
            print('Script is unable to connect :\n', str(e))
            sleep(10)
        else:
            if not influxdb_connected:
                print('Connected to  InfluxDB !')
            break
    return True

def main():
    influxdb_connected = False
    while 42:
        data = open_file()
        today = datetime.today()
        write_api = connect_to_influxdb()
        for url in data['website']:
            try:
                tmp = url['ssl']
            except KeyError:
                tmp = False
            if tmp:
                base_url = url['url']
                port = '443'
                hostname = format_url(base_url)
                context = ssl.create_default_context()
                try:
                    with socket.create_connection((hostname, port)) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            data = ssock.getpeercert()
                except ssl.SSLCertVerificationError:
                    expiration = datetime.now() - timedelta(days=1)
                    dns = ""
                else:
                    expiration = datetime.utcfromtimestamp(ssl.cert_time_to_seconds(data['notAfter']))
                    dns = str(data['subjectAltName'])
                    dns = dns.replace('(', '').replace(')', '').replace("'", '').replace('DNS', '').replace(' ', '')
                    dns = dns[1:]
                    dns = dns.split(',,')
                delta = expiration - today
                try:
                    tags = url['tags']
                except:
                    tags = []
                if write_api != None:
                    influxdb_connected = insert_to_influxdb(write_api, influxdb_connected, hostname, expiration, dns, delta, tags)
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