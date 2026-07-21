### Copyright 2020
### Riverbed Technology, inc
### This is an example of how to delete a device from NetIM given its sysname
### In this example the sysname of the device is specified in devices_to_delete.txt

# This script can be run directly and accepts one optional parameter to set the base URL and port
# Resource used:
# https://<base_url:port>/api/netim/v1/devices/

'''
Usage: 
python3 delete_device_list.py
python3 delete_device_list.py https://10.46.250.62:8543
'''

import sys
from utils import utils
from datetime import datetime
import json

test_output = False

# If device_id_list is empty then all devices will be deleted from the network
def delete_devices(base_url, device_id_list, session, test=False):
    url = base_url + "/api/netim/v1/devices/"
    data = {"objectIds":device_id_list}
    
    #Add mandatory parameters for bulk deletion
    parameters="excludeFromDiscovery=false&confirmDeleteAll=true"
    resp = None
    if test:
        print(f"{str(datetime.now())}: Dry run of delete on {url+parameters} with data {json.dumps(data)}")
    else:
        resp = session.delete(url+"?"+parameters,
            verify=False,
            data=json.dumps(data))
    return resp

def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    #get the list of sysnames
    sysname_list = utils.read_list_from_file("ExampleInput/devices_to_delete.txt")
    
    #Create a map of sysnames to device ids for each device in the network
    sysname_to_id_map = utils.get_sysname_device_id_map(base_url, session)
    devices_to_delete = list()
    for sysname in sysname_list:
        id_to_delete = sysname_to_id_map[sysname]
        if id_to_delete is not None and len(id_to_delete) > 0:
            devices_to_delete.append(id_to_delete)
        
    #Add the list of devices to the request data
    if len(devices_to_delete) > 0:
        delete_devices(base_url, devices_to_delete, session, test_output)

    session.close()

if __name__ == '__main__':
    main()