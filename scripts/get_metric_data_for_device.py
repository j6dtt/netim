### Copyright 2020
### Riverbed Technology, inc
### Get metric data by providing device ID and metric types

### This script uses two files to determine which metric data to retrieve
### metric_types.txt and device_metric_request_input.txt

### metric_types.txt ###
### Metric types to be retrieved are specified in metric_types.txt as
### METRIC_CLASS,metric1,metric2

### device_metric_request_input.txt ###
### The device list that will be queried is specified in device_metric_request_input.txt as
### sysname,metric class

# This script can be run directly and does not take any parameters
# Resources used:
# https://localhost:8543/swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data
# https://localhost:8543/api/netim/v1/devices/

'''
Usage: 
python3 get_metric_data_for_device.py
python3 get_metric_data_for_device.py https://10.46.250.62:8543
'''

import sys
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from utils import utils
    
def get_metric_class_dictionary(file_path):
    metric_class_to_metric_list_dict = dict()
    
    with open(file_path) as flat_file:
        for line in flat_file:
            if line.startswith("#") or len(line) == 0 or line.isspace():
                continue
            line_list = line.strip().replace('"','').split(',')
            metric_class = line_list[0]
            metric_list = line_list[1:]
            metric_class_to_metric_list_dict[metric_class] = metric_list
    return metric_class_to_metric_list_dict
    
def get_device_metric_request(sysname_dev_id_map, file_path):
    metric_class_to_device_list_dict = dict()
    with open(file_path) as flat_file:
        for line in flat_file:
            if line.startswith("#") or len(line) == 0 or line.isspace():
                continue
            line_list = line.strip().replace('"','').split(',')

            dev_id = sysname_dev_id_map[line_list[0]]
            if line_list[1] in metric_class_to_device_list_dict:
                metric_class_to_device_list_dict[line_list[1]].append(dev_id)
            else:
                metric_class_to_device_list_dict[line_list[1]] = [dev_id]
    return metric_class_to_device_list_dict

def get_metric_data(url, metric_class_to_device_list_dict, metric_class_to_metric_dict, session):
    endTime = int(time.time()*1000)
    startTime = endTime - 1000*60*60
    json_dict = dict()
    for metric_class in metric_class_to_device_list_dict:
        device_id_list = metric_class_to_device_list_dict[metric_class]
        metric_list = metric_class_to_metric_dict[metric_class]
        metric_request_data = {
                "startTime" : startTime, 
                "endTime" : endTime,
                "metricClass" : metric_class,
                "metrics" : metric_list,
                "elementIds" : device_id_list,
                "sortOrder" : "ASCENDING",
                "elementType" : "VNES_OE",
                "includeRaw" : "true",
                "rollupCriterias": ["aggregateAvgRollup"],
                "aggregations": [],
                "includeSamples": "true",
                "pageSize" : "1000"
            }
        
        # https://localhost:8543/swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data
        resp = session.post(url, verify=False, data=json.dumps(metric_request_data))
        if resp is not None: 
            if resp.status_code >= 200 and resp.status_code < 300:
                resp_text = resp.text
                json_dict[metric_class] = json.loads(resp_text)
            else:
                print(f"Unable to retrieve resource. Status code: {resp.status_code}")
        else:
            print(f"Unable to retrieve resource from URL: {resource_url}")
    return json_dict

# Get metric data for the last hour for the specified devices
def write_metric_data_to_file(url, metric_class_to_device_list_dict, metric_class_to_metric_dict, filename, session):
    json_dict = get_metric_data(url, metric_class_to_device_list_dict, metric_class_to_metric_dict, session)
    pretty_print_json_dict = json.dumps(json_dict, indent=4)
    file_handle = open(filename, 'w+')
    file_handle.write(pretty_print_json_dict)

def main():
    base_url = utils.get_base_url(sys.argv)
    metric_url = base_url + "/swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data"
    session = utils.get_session()
    
    sysname_dev_id_map = utils.get_sysname_device_id_map(base_url, session)
    metric_class_to_metric_dict = get_metric_class_dictionary("ExampleInput/metric_types.txt")
    metric_class_to_device_list_dict = get_device_metric_request(sysname_dev_id_map, "ExampleInput/device_metric_request_input.txt")
    
    write_metric_data_to_file(metric_url, metric_class_to_device_list_dict, metric_class_to_metric_dict, "ExampleOutput/metric_data_example_output.txt", session)
    
    session.close()

if __name__ == '__main__':
    main()