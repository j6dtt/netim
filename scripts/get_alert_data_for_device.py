### Copyright 2020
### Riverbed Technology, inc
### Get device alert data for given devices

### This script uses ExampleInput/device_alert_request_input.txt

### device_alert_request_input.txt ###
### sysname

# Resources used:
# /swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data
# /api/netim/v1/devices
# /api/netim/v1/devices/<id>/interfaces
# /api/netim/v1/alert-profiles

'''
Usage: 
python3 get_alert_data_for_device.py
python3 get_alert_data_for_device.py https://10.46.250.62:8543
'''

import sys
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from utils import utils
from utils import metric_data_utils

def get_metric_class_dictionary():
    metric_class_to_metric_field_list_dict = {
        "DEV_ALERT_EVENTS_DETAIL" : ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"],
        "IFC_ALERT_EVENTS_DETAIL" : ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"],
        "DEV_SYSLOG_EVENTS_DETAIL" : ["Agent","Severity","Data","AdditionalData"],
        "DEV_TRAP_EVENTS_DETAIL" : ["Agent","TrapOID","Category","Severity","TrapDisplayName","Data","AdditionalData"],
        "IFC_SYSLOG_EVENTS_DETAIL" : ["Agent","Severity","Data","AdditionalData"],
        "IFC_TRAP_EVENTS_DETAIL" : ["Agent","TrapOID","Category","Severity","TrapDisplayName","Data","AdditionalData"]
    }
    return metric_class_to_metric_field_list_dict
    
def get_metric_data(session, base_url, metric_class_to_device_list_dict, metric_class_to_metric_dict, 
                    obj_name_id_dict, dev_interface_id_name_dict, alert_profile_name_id_dict):
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
            "rollupCriterias": ["RAW"],
            "aggregations": [],
            "includeSamples": "true",
            "pageSize" : "1000"
        }
        
        metric_data_utils.get_alert_syslog_trap_metric_data(session, base_url, metric_request_data, json_dict, obj_name_id_dict, 
                    dev_interface_id_name_dict, alert_profile_name_id_dict)
    return json_dict


def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    sysname_dev_id_map = utils.get_sysname_device_id_map(base_url, session)
    dev_interface_id_name_dict = {}
    alert_profile_name_id_dict = utils.get_alert_profile_name_id_map(base_url, session)

    metric_class_to_metric_dict = get_metric_class_dictionary()
    metric_class_to_device_list_dict = metric_data_utils.get_metric_class_object_list_map(metric_class_to_metric_dict, 
                                        sysname_dev_id_map, "ExampleInput/device_alert_request_input.txt")
    
    alerts_by_object_dict = get_metric_data(session, base_url, 
        metric_class_to_device_list_dict, metric_class_to_metric_dict, 
        sysname_dev_id_map, dev_interface_id_name_dict, alert_profile_name_id_dict)
    
    '''
    # In case you collect data from Postman or other REST API tool, you can create a file with the following format:
    # {
    # "DEV_ALERT_EVENTS_DETAIL": <json response from the REST API>,
    # "IFC_ALERT_EVENTS_DETAIL": <json response from the REST API>,
    # }    
    alerts_by_object_dict = metric_data_utils.get_alert_syslog_trap_from_file("device_alert_data_example_output_ref.txt", 
        session, base_url, sysname_dev_id_map, dev_interface_id_name_dict, alert_profile_name_id_dict)
    '''

    utils.write_metric_data_to_file(alerts_by_object_dict, "ExampleOutput/device_alert_data_example_output.txt")
    
    session.close()

if __name__ == '__main__':
    main()