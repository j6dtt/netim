### Copyright 2020
### Riverbed Technology, inc
### Get test alert data for given tests

### This script uses ExampleInput/test_alert_request_input.txt

### test_alert_request_input.txt ###
### grpname

# Resources used:
# /swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data
# /api/netim/v1/tests/
# /api/netim/v1/alert-profiles

'''
Usage: 
python3 get_alert_data_for_test.py
python3 get_alert_data_for_test.py https://10.46.250.62:8543
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
        "AM_DATABASE_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_DATABASE", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
        "AM_DNS_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_DNS", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
        "AM_HTTP_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_HTTP", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
        "AM_LDAP_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_LDAP", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
        "AM_PING_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_PING", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
        "AM_SCRIPT_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_SCRIPT", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
        "AM_SELENIUM_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_SELENIUM", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
        "AM_TCPPORT_TEST_ALERT_EVENTS_DETAIL": ("VNES_TEST_TCPPORT", ["ProfileId", "AdditionalData", "AlertId", "AlertSeverity", "Data", "NumTimesSeen", "AlertState"]),
    }
    return metric_class_to_metric_field_list_dict
    
def get_metric_data(session, base_url, metric_class_to_test_list_dict, metric_class_to_metric_dict,
                    testname_id_map, alert_profile_name_id_dict):
    endTime = int(time.time()*1000)
    startTime = endTime - 1000*60*60
    json_dict = dict()
    for metric_class in metric_class_to_metric_dict.keys():
        test_id_list = metric_class_to_test_list_dict[metric_class]
        (test_type, metric_list) = metric_class_to_metric_dict[metric_class]
        metric_request_data = {
                "startTime" : startTime, 
                "endTime" : endTime,
                "metricClass" : metric_class,
                "metrics" : metric_list,
                "elementIds" : test_id_list,
                "sortOrder" : "ASCENDING",
                "elementType" : test_type,
                "includeRaw" : "true",
                "rollupCriterias": ["RAW"],
                "aggregations": [],
                "includeSamples": "true",
                "pageSize" : "1000"
            }
        
        metric_data_utils.get_alert_syslog_trap_metric_data(session, base_url, metric_request_data, json_dict, 
                    testname_id_map, None, alert_profile_name_id_dict)

    return json_dict


def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    testname_id_map = utils.get_testname_id_map(base_url, session)
    alert_profile_name_id_dict = utils.get_alert_profile_name_id_map(base_url, session)

    metric_class_to_metric_dict = get_metric_class_dictionary()
    metric_class_to_test_list_dict = metric_data_utils.get_metric_class_object_list_map(metric_class_to_metric_dict, 
                                        testname_id_map, "ExampleInput/test_alert_request_input.txt")
    
    alerts_by_object_dict = get_metric_data(session, base_url, 
        metric_class_to_test_list_dict, metric_class_to_metric_dict, 
        testname_id_map, alert_profile_name_id_dict)

    '''
    # In case you collect data from Postman or other REST API tool, you can create a file with the following format:
    # {
    # "AM_PING_TEST_ALERT_EVENTS_DETAIL": <json response from the REST API>,
    # "AM_HTTP_TEST_ALERT_EVENTS_DETAIL": <json response from the REST API>
    # }    
    alerts_by_object_dict = metric_data_utils.get_alert_syslog_trap_from_file("test_alert_data_example_output_ref.txt", 
        session, base_url, testname_id_map, None, alert_profile_name_id_dict)
    '''

    utils.write_metric_data_to_file(alerts_by_object_dict, "ExampleOutput/test_alert_data_example_output.txt")
    
    session.close()

if __name__ == '__main__':
    main()