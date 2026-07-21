### Copyright 2020
### Riverbed Technology, inc
### This is an example of retrieving all devices in batches, filtering them based on custom attributes, and writing them to a file
### Custom attributes are read from custom_attribute_filter.txt
# This script can be called directly and optionally accepts one parameter to set the base URL and port
# Resources used:
# https://<base_url:port>/api/netim/v1/custom-attribute-values/
# https://<base_url:port>/api/netim/v1/devices/

'''
Usage: 
python3 get_devices_with_custom_attributes.py
python3 get_devices_with_custom_attributes.py https://10.46.250.62:8543
'''

import sys
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import json
from utils import utils

def write_devices_to_file(url, device_id_list, filename, session):
    with open(filename,'w+',encoding = 'utf-8') as file_handle:
        netim_device_url = url + "/api/netim/v1/devices/"
        for device_id in device_id_list:
            final_url = netim_device_url + str(device_id)
            resp = session.get(final_url, verify=False)
            resp_text = resp.text
            json_dict = json.loads(resp_text)

            pretty_json_dict = json.dumps(json_dict, indent=4)
            file_handle.write(pretty_json_dict)

def get_devices_with_attributes(url, cust_attr_name_list, session):
    cust_attr_val_url = url + "/api/netim/v1/custom-attribute-values/"
    dev_id_set = set()

    # https://localhost:8543/api/netim/v1/custom-attribute-values/
    json_dict = utils.get_initial_json_from_resource(cust_attr_val_url, session)
    item_list = json_dict['items']
    for item in item_list:
        cust_attr_name = item["attributeDefinition"]["name"]
        if cust_attr_name in cust_attr_name_list:
            cust_attr_assoc_dev_list = item["deviceIds"]
            dev_id_set.update(cust_attr_assoc_dev_list)
            
    if "meta" in json_dict:
        meta = json_dict["meta"]
        while meta["next_offset"] < meta["total"]:
            json_dict = get_json_from_resource_page(resource_url, meta["limit"], meta["next_offset"], session)
            meta = json_dict["meta"]
            item_list = json_dict['items']
            for item in item_list:
                cust_attr_name = item["attributeDefinition"]["name"]
                if cust_attr_name in cust_attr_name_list:
                    cust_attr_assoc_dev_list = item["deviceIds"]
                    dev_id_set.update(cust_attr_assoc_dev_list)
    
    return list(dev_id_set)

def main():
    url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    #Get the list of custom attribute names to filter on
    cust_attr_name_list = utils.read_list_from_file("ExampleInput/custom_attribute_filter.txt")
    device_id_list = get_devices_with_attributes(url, cust_attr_name_list, session)
    write_devices_to_file(url, device_id_list, "get_devices_with_custom_attributes_example_output.txt", session)
    
    session.close()

if __name__ == '__main__':
    main()