### Copyright 2020
### Riverbed Technology, inc
### This is an example of adding a device via POST request. Alternatively you can append the IP address of 
### a device to /<NetIM install dir>/input/AutoDiscovery/seed.txt and run discovery

### Devices to add are specified in add_new_devices.txt in the following format:
# Device name, access address, device driver, cli username

# This script can be run directly and accepts one optional parameter to set the base URL and port
# Resource used:
# https://<base_url:port>/api/netim/v1/devices

'''
Usage: 
python3 add_devices.py
python3 add_devices.py https://10.46.250.62:8543
'''

import sys
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import json
from utils import utils

test_output = False

def read_device_from_file(file_path):
    dev_list = list()
    with open(file_path) as flat_file:
        for line in flat_file:
            if line.startswith("#") or len(line) == 0 or line.isspace():
                continue
            line = line.replace('"','')
            line = line.strip()
            line_list = line.split(',')
            dev_dictionary = dict()
            dev_dictionary["device name"] = line_list[0]
            dev_dictionary["access address"] = line_list[1]
            dev_dictionary["device driver"] = line_list[2]
            dev_dictionary["cli username"] = line_list[3]
            dev_list.append(dev_dictionary)
    return dev_list


'''
Expects a list of dictionaries with device name, access address, device driver name, cli username
This will add the device for later collection and update. Device access info object defined in method. 
'''
def add_device(url, dev_list, session, test=False):
    items = list()
    for dev_dictionary in dev_list:
        device_name = dev_dictionary["device name"]
        access_address = dev_dictionary["access address"]
        device_driver = dev_dictionary["device driver"]
        cli_username = dev_dictionary["cli username"]
        
        item = dict()
        item["name"] = device_name
        item["displayName"] = device_name
        item["deviceName"] = device_name
        item["accessAddress"] = access_address
        item["description"] = "none"
        deviceAccessInfo = dict()
        deviceAccessInfo["name"] = device_name
        deviceAccessInfo["displayName"] = device_name
        deviceAccessInfo["active"] = True
        deviceAccessInfo["activeCLIConfigCollection"] = True
        deviceAccessInfo["activeMIBConfigCollection"] = True
        deviceAccessInfo["activeWMIConfigCollection"] = False
        deviceAccessInfo["activeMetricsCollection"] = False
        deviceAccessInfo["activeAWSConfigCollection"] = False
        deviceAccessInfo["deviceDriver"] = device_driver
        deviceAccessInfo["accessAddress"] = access_address
        deviceAccessInfo["cliUsername"] = cli_username
        deviceAccessInfo["hasCliPassword"] = True
        deviceAccessInfo["hasCliPrivPassword"] = False
        deviceAccessInfo["cliLoginScript"] = "InitPrompt"
        deviceAccessInfo["cliAccessMethod"] = 3
        deviceAccessInfo["snmpVersion"] = 1
        deviceAccessInfo["hasSnmpCommunityString"] = True
        deviceAccessInfo["hasSnmpV3AuthPassword"] = False
        deviceAccessInfo["hasSnmpV3PrivacyPassword"] = False
        deviceAccessInfo["wmiUsername"] = "none"
        deviceAccessInfo["wmiDomain"] = "none"
        deviceAccessInfo["awsInstanceId"] = "none"
        deviceAccessInfo["awsAccessKeyId"] = "none"
        deviceAccessInfo["awsRegion"] = "none"
        deviceAccessInfo["awsSecretAccessKey"] = "none"
        item["deviceAccessInfo"] = deviceAccessInfo
        items.append(item)
        
    json_dict = {"items":items}
    # https://localhost:8543/api/netim/v1/devices
    if test:
        with open("add_device_json_dump.txt",'w',encoding = 'utf-8') as file_handle:
            pretty_json_dict = json.dumps(json_dict, indent=4)
            file_handle.write(pretty_json_dict)
    else:
        resp = session.post(url, verify=False, json=json_dict)

def main():
    base_url = utils.get_base_url(sys.argv)
    url = base_url + "/api/netim/v1/devices"
    session = utils.get_session()
    
    dev_list = read_device_from_file("ExampleInput/add_new_devices.txt")
    add_device(url, dev_list, session, test_output)
    
    session.close()

if __name__ == '__main__':
    main()