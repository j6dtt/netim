### Copyright 2020
### Riverbed Technology, inc
### This is an example of retrieving all devices in batches and writing any with a matching vendor to a file
### Vendors are read one per line from vendor_list.txt
### Vendor names must exactly match what is in NetIM.

# This script can be run directly and accepts one optional parameter to set the base URL and port
# Uses the following resource:
# https://<base_url:port>/api/netim/v1/devices

'''
Usage: 
python3 get_devices_by_vendor.py
python3 get_devices_by_vendor.py https://10.46.250.62:8543
'''

import sys
from utils import utils

test_output = False

def write_device_tuples_to_file(filename, device_tuple_list):
    file_handle = open(filename, 'w+')
    
    for device in device_tuple_list:
        file_handle.write(str(device) + '\n')

def get_matching_devices(url, vendor_list, session, test=False):
    api_url = url + "/api/netim/v1/devices"
    json_dict = utils.get_initial_json_from_resource(api_url, session)
    
    device_list = list()
    vendor_list = [vendor.lower() for vendor in vendor_list]
    item_list = json_dict['items']
    for item in item_list:
        try:
            device_vendor = item['vendor']
            if device_vendor.lower() in vendor_list:
                try:
                    device_ip = item['accessAddress']
                except:
                    device_ip = ""
                try:
                    device_name = item['sysName']
                except:
                    device_name = item['deviceName']
                device_tuple = (device_name,device_ip,device_vendor)
                device_list.append(device_tuple)
        except:
            device_vendor = ""

    if "meta" in json_dict:
        meta = json_dict["meta"]
        while meta["total"] != meta["next_offset"]:
            json_dict = utils.get_json_from_resource_page(api_url, meta["limit"], meta["next_offset"], session, test)
            meta = json_dict["meta"]
            item_list = json_dict['items']
            for item in item_list:
                try:
                    device_vendor = item['vendor']
                    if device_vendor.lower() in vendor_list:
                        try:
                            device_ip = item['accessAddress']
                        except:
                            device_ip = ""
                        try:
                            device_name = item['sysName']
                        except:
                            device_name = item['deviceName']
                        device_tuple = (device_name,device_ip,device_vendor)
                        device_list.append(device_tuple)
                except:
                    device_vendor = ""

    
    return device_list

def main():
    url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    vendor_list = utils.read_list_from_file("ExampleInput/vendor_list.txt")
    
    device_list = get_matching_devices(url, vendor_list, session, test_output)
    write_device_tuples_to_file("ExampleOutput/get_devices_by_vendor_output.txt", device_list)
    
    session.close()

if __name__ == '__main__':
    main()