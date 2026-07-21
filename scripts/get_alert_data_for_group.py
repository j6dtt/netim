### Copyright 2020
### Riverbed Technology, inc
### Get group alert data for given groups

### This script uses ExampleInput/group_alert_request_input.txt

### group_alert_request_input.txt ###
### grpname

# Resources used:
# /swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data
# /api/netim/v1/groups/
# /api/netim/v1/alert-profiles

'''
Usage: 
python3 get_alert_data_for_group.py
python3 get_alert_data_for_group.py https://10.46.250.62:8543
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
        "GRP_ALERT_EVENTS_DETAIL" : ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"],
    }
    return metric_class_to_metric_field_list_dict
    
def get_metric_data(session, base_url, metric_class_to_group_list_dict, metric_class_to_metric_dict, 
                    groupname_id_map, alert_profile_name_id_dict):
    endTime = int(time.time()*1000)
    startTime = endTime - 1000*60*60
    json_dict = dict()
    for metric_class in metric_class_to_group_list_dict:
        group_id_list = metric_class_to_group_list_dict[metric_class]
        metric_list = metric_class_to_metric_dict[metric_class]
        metric_request_data = {
                "startTime" : startTime, 
                "endTime" : endTime,
                "metricClass" : metric_class,
                "metrics" : metric_list,
                "elementIds" : group_id_list,
                "sortOrder" : "ASCENDING",
                "elementType" : "VNES_GROUP",
                "includeRaw" : "true",
                "rollupCriterias": ["RAW"],
                "aggregations": [],
                "includeSamples": "true",
                "pageSize" : "1000"
            }
        
        metric_data_utils.get_alert_syslog_trap_metric_data(session, base_url, metric_request_data, json_dict,  
                    groupname_id_map, None, alert_profile_name_id_dict)

    return json_dict


def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    groupname_id_map = utils.get_groupname_id_map(base_url, session)
    alert_profile_name_id_dict = utils.get_alert_profile_name_id_map(base_url, session)

    metric_class_to_metric_dict = get_metric_class_dictionary()
    metric_class_to_group_list_dict = metric_data_utils.get_metric_class_object_list_map(metric_class_to_metric_dict, 
                                        groupname_id_map, "ExampleInput/group_alert_request_input.txt")
    
    alerts_by_object_dict = get_metric_data(session, base_url, 
        metric_class_to_group_list_dict, metric_class_to_metric_dict, 
        groupname_id_map, alert_profile_name_id_dict)

    '''
    # In case you collect data from Postman or other REST API tool, you can create a file with the following format:
    # {
    # "GRP_ALERT_EVENTS_DETAIL": <json response from the REST API>
    # }    
    alerts_by_object_dict = metric_data_utils.get_alert_syslog_trap_from_file("group_alert_data_example_output_ref.txt", 
        session, base_url, groupname_id_map, None, alert_profile_name_id_dict)
    '''

    utils.write_metric_data_to_file(alerts_by_object_dict, "ExampleOutput/group_alert_data_example_output.txt")
    
    session.close()

if __name__ == '__main__':
    main()