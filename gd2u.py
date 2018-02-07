#!/usr/bin/python3
import requests
import yaml

from sys import exit
from time import sleep

def readConfigFile(file):
    try:
        with open(file, 'r') as f:
            configs = yaml.load(f)
        return configs
    except:
        exit("Unable to parse gd2u configuration file")

def getIP():
    url = 'https://api.ipify.org'
    try:
        return requests.get(url).text
    except:
        exit("Unable to get current external IP address")

def ipChanged(ip):
    if ip != getIP():
        return True
    else:
        return False

def updateRecord(ip, domain, username, password):
    url = "https://{username}:{password}@domains.google.com/nic/update".format(username=username, password=password)
    data = {"hostname" : domain, "myip" : ip}
    try:
        r = requests.post(url, data=data)
    except:
        exit("Unable to update Google Domains Dynamic DNS Record")

def run():
    currentIP = '0.0.0.0'
    configs = readConfigFile('gd2u.conf')

    while True:
        if ipChanged(currentIP):
            for domain in configs.get('domains'):
                updateRecord(currentIP, domain.get('subdomain'), domain.get('username'), domain.get('password'))
        sleep(configs.get('global').get('check_interval'))

if __name__ == "__main__":
    run()
