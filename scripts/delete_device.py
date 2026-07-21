### Copyright 2020
### Riverbed Technology, inc
### This is an example of how to delete a device from NetIM given its sysname or device name
### In this example the sysname of the device is specified in devices_to_delete.txt

# This script can be run directly and accepts one optional parameter to set the base URL and port
# Resource used:
# https://<base_url:port>/api/netim/v1/devices

'''
Usage: 
python3 delete_device.py
python3 delete_device.py https://10.46.250.62:8543
'''

import sys
from utils import utils
from datetime import datetime
import json

test_output = False

def delete_device(base_url, device_id, session, test=False):
    parameters = {"id":str(device_id),"excludeFromDiscovery":"false"}
    url = base_url + "/api/netim/v1/devices/"
    resp = None
    if test:
        print(f"{str(datetime.now())}: Dry run of delete on {url}{device_id} with parameters {json.dumps(parameters)}")
    else:
        resp = session.delete(url + str(device_id),verify=False,data=json.dumps(parameters))
    return resp

# This is an example of device deletion
# This script will log in to NetIM core and delete the device with the given ID. 
def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    #get the list of sysnames
    sysname_list = utils.read_list_from_file("ExampleInput/devices_to_delete.txt")
    
    #Create a map of sysnames to device ids for each device in the network
    sysname_to_id_map = utils.get_sysname_device_id_map(base_url, session)
    for sysname in sysname_list:
        individual_id_to_delete = sysname_to_id_map[sysname]
        
        #delete the device. Note that this is only an efficient method of deleting a single device
        #To efficiently delete multiple devices see delete_device_list_example.py 
        delete_device(base_url, individual_id_to_delete, session, test_output)
    session.close()

if __name__ == '__main__':
    main()