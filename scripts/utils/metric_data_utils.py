### Copyright 2020
### Riverbed Technology, inc
### Utility functions to process data returned by the network metric data REST API

import json
from utils import utils

def get_metric_field_index(metric_data_dict, metric_field_name):
    metric_field_index = -1
    metric_names_list = None
    try:
        metric_names_list = metric_data_dict["metricNames"]
    except KeyError:
        print("metric data dict did not include metricNames")

    if (metric_names_list != None):
        try:
            metric_field_index = metric_names_list.index(metric_field_name)
        except ValueError:
            print("metricNames did not include field: " + metric_field_name)
    
    return metric_field_index

def get_alert_severity_enum_map(metric_data_dict):
    alert_severity_enum_dict = None
    try:
        alert_severity_enum_dict = metric_data_dict["metricToMetaInfoMap"]["AlertSeverity"]["valueEnumMap"]
    except KeyError:
        print("metric data dict did not include metricToMetaInfoMap")
    
    return alert_severity_enum_dict

def get_alert_state_enum_map(metric_data_dict):
    alert_state_enum_dict = None
    try:
        alert_state_enum_dict = metric_data_dict["metricToMetaInfoMap"]["AlertState"]["valueEnumMap"]
    except KeyError:
        print("metric data dict did not include metricToMetaInfoMap")
    
    return alert_state_enum_dict    

def convert_data_additional_data_json_to_dict (metric_data_resp_dict):
    if (metric_data_resp_dict == None):
        return

    metric_data_dict = None
    try:
        metric_data_dict = metric_data_resp_dict["metricData"]
    except KeyError:
        print("response did not include metricData")
    
    if (metric_data_dict == None):
        return

    # Get indices of AdditionalData and Data
    additional_data_index = get_metric_field_index(metric_data_dict, "AdditionalData")
    data_index = get_metric_field_index(metric_data_dict, "Data")
    if (additional_data_index == -1 or data_index == -1):
        return

    metric_element_data_list = None
    try:
        metric_element_data_list = metric_data_dict["metricElementDataList"]
    except KeyError:
        print("metric_data_dict did not include metricElementDataList")
        return

    for metric_element_data_dict in metric_element_data_list:
        timestamp_to_values_dict = None
        try:
            timestamp_to_values_dict = metric_element_data_dict["timestampToValuesMap"]
        except KeyError:
            print("metric_element_data_dict (element: %s) did not include timestampToValuesMap" % (str(metric_element_data_dict)))
            continue

        for timestamp in timestamp_to_values_dict.keys():
            metric_data_list = timestamp_to_values_dict[timestamp]
            additional_data = metric_data_list[additional_data_index]
            if (additional_data != None):
                metric_data_list[additional_data_index] = json.loads(additional_data)
            data = metric_data_list[data_index]
            if (data != None):
                metric_data_list[data_index] = json.loads(data)

    return

def get_alert_severity_display_string(alert_severity_enum_dict, alert_sev_metric_value):
    alert_sev_int_str = str(int(alert_sev_metric_value))
    alert_severity_display_string = alert_sev_int_str
    try:
        alert_severity_display_string = alert_severity_enum_dict[alert_sev_int_str]
    except KeyError:
        pass

    return alert_severity_display_string

def get_alert_state_display_string(alert_state_enum_dict, alert_state_metric_value):
    alert_state_int_str = str(int(alert_state_metric_value))
    alert_state_display_string = alert_state_int_str
    try:
        alert_state_display_string = alert_state_enum_dict[alert_state_int_str]
    except KeyError:
        pass
        
    return alert_state_display_string

def get_obj_child_name(session, base_url, object_id, child_id, child_obj_id_name_dict):
    child_name = None
    if (child_obj_id_name_dict != None):
        try:
            child_name = child_obj_id_name_dict [child_id]
        except KeyError:
            obj_children_dict = utils.get_device_interface_id_name_map(base_url, session, object_id)    
            if (obj_children_dict != None):
                child_obj_id_name_dict.update(obj_children_dict)
                try: 
                    child_name = child_obj_id_name_dict [child_id]
                except KeyError:
                    pass

    if (child_name == None):
        child_name = child_id
    
    return child_name

def get_object_name(session, base_url, obj_name_id_dict, child_obj_id_name_dict, element_id_object_info_dict, element_id):
    object_name = element_id

    object_info_dict = None
    try:
        object_info_dict = element_id_object_info_dict[element_id]
    except KeyError:
        return (None, None, None, None, element_id)

    # object_id is obtained from "parentObjectId" if present, if not then from "objectId" 
    object_id = None
    child_id = None
    try:
        object_id = object_info_dict["parentObjectId"]
        child_id = object_info_dict["objectId"]
    except KeyError:
        try:
            object_id = object_info_dict["objectId"]
        except KeyError:
            return (None, None, None, None, element_id)
    
    # Use the object id as the name if it is not found in the obj_name_id_dict
    object_name = object_id

    # obtain the name from the obj_name_id_dict
    for (obj_name, obj_id) in obj_name_id_dict.items():
        if (obj_id == object_id):
            object_name = obj_name
            break

    obj_display_name = object_name
    child_name = None
    if (child_id != None):
        child_name = get_obj_child_name(session, base_url, object_id, child_id, child_obj_id_name_dict)
        obj_display_name = object_name + " > " + child_name

    return (object_name, object_id, child_name, child_id, obj_display_name)

def get_alert_profile_name_by_id(alert_profile_name_id_dict, req_profile_id):
    req_profile_id = str(int(req_profile_id))

    # obtain the profile name from the alert_profile_name_id_dict
    req_profile_name = req_profile_id
    for (profile_name, profile_id) in alert_profile_name_id_dict.items():
        if (req_profile_id == profile_id):
            req_profile_name = profile_name
            break

    return req_profile_name

def get_operator_display(operator_str):
    operator_map = {
        "&gt;" : ">",
        "&ge;" : ">=",
        "&lt;" : "<",
        "&le;" : "<=",
    }
    op_display_str = operator_str
    try:
        op_display_str = operator_map[operator_str]
    except KeyError:
        pass
    return op_display_str      

def create_alert_data_row_dict(object_name, object_id, child_name, child_id, obj_display_name, timestamp, 
                    profile_name, metric_class, alert_severity, alert_state, alert_data_dict, additional_data_dict):
    alert_data_row_dict = {
        "object_name" : obj_display_name,
        "timestamp" : timestamp, 
        "profile_name" : profile_name, 
        "category" : metric_class,
        "alert_severity" : alert_severity,
        "alert_state" : alert_state,
    }
    if (object_id != None and child_id != None):
        alert_data_row_dict ["object_id"] = child_id
        alert_data_row_dict ["parent_object_id"] = object_id
    elif (object_id != None):
        alert_data_row_dict ["object_id"] = object_id

    alert_data_row_dict ["metric_class"] = "-"
    try:
        alert_data_row_dict ["metric_class"] = alert_data_dict["Metric Class"]
    except KeyError:
        pass

    alert_data_row_dict ["metric_field"] = "-"
    try:
        alert_data_row_dict ["metric_field"] = alert_data_dict["Metric Field"]
    except KeyError:
        pass

    alert_data_row_dict ["metric_value"] = "-"
    try:
        alert_data_row_dict ["metric_value"] = alert_data_dict["Metric Value"]
    except KeyError:
        pass

    alert_data_row_dict ["metric_violation"] = '-'
    if (alert_severity != "Normal" and alert_state != "Inactive"):
        try:
            operator_str = get_operator_display(alert_data_dict["Operator"])
            threshold_str = alert_data_dict["Threshold"]
            alert_data_row_dict ["metric_violation"] = operator_str + threshold_str
        except KeyError:
            pass

    # Add additional data to the alert row
    alert_data_row_dict["additional_data"] = additional_data_dict

    return alert_data_row_dict


def process_alert_events_detail(session, base_url, obj_name_id_dict, child_obj_id_name_dict, metric_data_resp_dict, 
                                    alert_profile_name_id_dict, metric_class):
    alert_data_by_object_dict = None

    if (metric_data_resp_dict == None):
        return alert_data_by_object_dict

    try:
        element_id_object_info_dict = metric_data_resp_dict["elementIdToObjectInfoMap"]
    except KeyError:
        print("response did not include elementIdToObjectInfoMap")
        return alert_data_by_object_dict


    metric_data_dict = None
    try:
        metric_data_dict = metric_data_resp_dict["metricData"]
    except KeyError:
        print("response did not include metricData")
        
    if (metric_data_dict == None):
        return alert_data_by_object_dict

    # Get the alert severity enum dict
    alert_severity_enum_dict = get_alert_severity_enum_map(metric_data_dict)
    alert_state_enum_dict = get_alert_state_enum_map(metric_data_dict)
    if (alert_severity_enum_dict == None or alert_state_enum_dict == None):
        print("could not find severity / state enums")
        return alert_data_by_object_dict

    # Get metric field indices
    profile_id_index = get_metric_field_index(metric_data_dict, "ProfileId")
    alert_id_index = get_metric_field_index(metric_data_dict, "AlertId")
    alert_sev_index = get_metric_field_index(metric_data_dict, "AlertSeverity")
    num_times_seen_index = get_metric_field_index(metric_data_dict, "NumTimesSeen")
    alert_state_index = get_metric_field_index(metric_data_dict, "AlertState")
    additional_data_index = get_metric_field_index(metric_data_dict, "AdditionalData")
    data_index = get_metric_field_index(metric_data_dict, "Data")
    if (profile_id_index == -1 or alert_id_index == -1 or alert_sev_index == -1 or data_index == -1 or
        num_times_seen_index == -1 or additional_data_index == -1 or alert_state_index == -1):
        print("could not find metric field indices")
        return alert_data_by_object_dict

    try:
        metric_element_data_list = metric_data_dict["metricElementDataList"]
    except KeyError:
        print("metric_data_dict did not include metricElementDataList")
        return alert_data_by_object_dict

    # Create a dictionary to hold alerts by object
    alert_data_by_object_dict = {}
    for metric_element_data_dict in metric_element_data_list:
        element_id = None
        try:
            element_id = metric_element_data_dict["elementId"]
        except KeyError:
            print("metric_element_data_dict (element: %s) did not include elementId" % (str(metric_element_data_dict)))
            continue

        (object_name, object_id, child_name, child_id, obj_display_name) = get_object_name(
            session, base_url, obj_name_id_dict, child_obj_id_name_dict, element_id_object_info_dict, str(element_id))

        try:
            timestamp_to_values_dict = metric_element_data_dict["timestampToValuesMap"]
        except KeyError:
            print("metric_element_data_dict (element: %s) did not include timestampToValuesMap" % (str(metric_element_data_dict)))
            continue

        try:
            object_alert_list = alert_data_by_object_dict[obj_display_name]
        except KeyError:
            object_alert_list = []
            alert_data_by_object_dict[obj_display_name] = object_alert_list

        for timestamp in timestamp_to_values_dict.keys():
            metric_data_list = timestamp_to_values_dict[timestamp]
            profile_name = get_alert_profile_name_by_id(alert_profile_name_id_dict, metric_data_list[profile_id_index])
            alert_severity = get_alert_severity_display_string(alert_severity_enum_dict, metric_data_list[alert_sev_index])
            alert_state = get_alert_state_display_string(alert_state_enum_dict, metric_data_list[alert_state_index])
            additional_data_str = metric_data_list[additional_data_index]
            alert_data_str = metric_data_list[data_index]

            additional_data_dict = None
            if (additional_data_str != None):
                additional_data_dict = json.loads(additional_data_str)

            alert_data_dict = None
            if (alert_data_str != None):
                alert_data_dict = json.loads(alert_data_str)

            alert_row_dict = create_alert_data_row_dict(
                object_name, object_id, child_name, child_id, obj_display_name, timestamp, profile_name, 
                metric_class, alert_severity, alert_state, alert_data_dict, additional_data_dict
            )

            object_alert_list.append(alert_row_dict)

    return alert_data_by_object_dict

def get_syslog_severity_enum_map(metric_data_dict):
    syslog_severity_enum_dict = None
    try:
        syslog_severity_enum_dict = metric_data_dict["metricToMetaInfoMap"]["Severity"]["valueEnumMap"]
    except KeyError:
        print("metric data dict did not include metricToMetaInfoMap")
    
    return syslog_severity_enum_dict

def get_syslog_severity_display_string(syslog_severity_enum_dict, trap_sev_metric_value):
    trap_sev_int_str = str(int(trap_sev_metric_value))
    trap_severity_display_string = trap_sev_int_str
    try:
        trap_severity_display_string = syslog_severity_enum_dict[trap_sev_int_str]
    except KeyError:
        pass

    return trap_severity_display_string

def create_syslog_data_row_dict(object_name, object_id, child_name, child_id, obj_display_name, timestamp,
                metric_class, agent_name, syslog_severity, syslog_data_dict, additional_data_dict):
    syslog_data_row_dict = {
        "object_name" : obj_display_name,
        "timestamp" : timestamp, 
        "category" : metric_class,
        "severity" : syslog_severity,
    }
    if (object_id != None and child_id != None):
        syslog_data_row_dict ["object_id"] = child_id
        syslog_data_row_dict ["parent_object_id"] = object_id
    elif (object_id != None):
        syslog_data_row_dict ["object_id"] = object_id

    try:
        syslog_data_row_dict ["facility"] = syslog_data_dict["Facility"]
    except KeyError:
        pass

    try:
        syslog_data_row_dict ["remote_address"] = syslog_data_dict["Remote Address"]
    except KeyError:
        pass

    try:
        syslog_data_row_dict ["syslog_severity"] = syslog_data_dict["Syslog Severity"]
    except KeyError:
        pass

    # Add additional data to the syslog row
    syslog_data_row_dict["additional_data"] = additional_data_dict

    return syslog_data_row_dict


def process_syslog_events_detail(session, base_url, obj_name_id_dict, child_obj_id_name_dict, 
                                    metric_data_resp_dict, metric_class):
    syslog_data_by_object_dict = None

    if (metric_data_resp_dict == None):
        return syslog_data_by_object_dict

    try:
        element_id_object_info_dict = metric_data_resp_dict["elementIdToObjectInfoMap"]
    except KeyError:
        print("response did not include elementIdToObjectInfoMap")
        return syslog_data_by_object_dict


    metric_data_dict = None
    try:
        metric_data_dict = metric_data_resp_dict["metricData"]
    except KeyError:
        print("response did not include metricData")

    if (metric_data_dict == None):
        return syslog_data_by_object_dict

    # Get the syslog severity enum dict
    syslog_severity_enum_dict = get_syslog_severity_enum_map(metric_data_dict)
    if (syslog_severity_enum_dict == None):
        print("could not find severity enum")
        return syslog_data_by_object_dict

    # Get metric field indices
    agent_index = get_metric_field_index(metric_data_dict, "Agent")
    severity_index = get_metric_field_index(metric_data_dict, "Severity")
    additional_data_index = get_metric_field_index(metric_data_dict, "AdditionalData")
    data_index = get_metric_field_index(metric_data_dict, "Data")
    if (agent_index == -1 or severity_index == -1 or data_index == -1 or additional_data_index == -1):
        print("could not find metric field indices")
        return syslog_data_by_object_dict

    try:
        metric_element_data_list = metric_data_dict["metricElementDataList"]
    except KeyError:
        print("metric_data_dict did not include metricElementDataList")
        return syslog_data_by_object_dict

    # Create a dictionary to hold syslogs by object
    syslog_data_by_object_dict = {}
    for metric_element_data_dict in metric_element_data_list:
        element_id = None
        try:
            element_id = metric_element_data_dict["elementId"]
        except KeyError:
            print("metric_element_data_dict (element: %s) did not include elementId" % (str(metric_element_data_dict)))
            continue

        (object_name, object_id, child_name, child_id, obj_display_name) = get_object_name(
            session, base_url, obj_name_id_dict, child_obj_id_name_dict, element_id_object_info_dict, str(element_id))

        try:
            timestamp_to_values_dict = metric_element_data_dict["timestampToValuesMap"]
        except KeyError:
            print("metric_element_data_dict (element: %s) did not include timestampToValuesMap" % (str(metric_element_data_dict)))
            continue

        try:
            object_syslog_list = syslog_data_by_object_dict[obj_display_name]
        except KeyError:
            object_syslog_list = []
            syslog_data_by_object_dict[obj_display_name] = object_syslog_list

        for timestamp in timestamp_to_values_dict.keys():
            metric_data_list = timestamp_to_values_dict[timestamp]
            agent_name = metric_data_list[agent_index]
            syslog_severity = get_syslog_severity_display_string(syslog_severity_enum_dict, metric_data_list[severity_index])
            additional_data_str = metric_data_list[additional_data_index]
            syslog_data_str = metric_data_list[data_index]

            additional_data_dict = None
            if (additional_data_str != None):
                additional_data_dict = json.loads(additional_data_str)

            syslog_data_dict = None
            if (syslog_data_str != None):
                syslog_data_dict = json.loads(syslog_data_str)

            syslog_row_dict = create_syslog_data_row_dict(
                object_name, object_id, child_name, child_id, obj_display_name, timestamp,
                metric_class, agent_name, syslog_severity, syslog_data_dict, additional_data_dict
            )

            object_syslog_list.append(syslog_row_dict)

    return syslog_data_by_object_dict

def get_trap_severity_enum_map(metric_data_dict):
    trap_severity_enum_dict = None
    try:
        trap_severity_enum_dict = metric_data_dict["metricToMetaInfoMap"]["Severity"]["valueEnumMap"]
    except KeyError:
        print("metric data dict did not include metricToMetaInfoMap")
    
    return trap_severity_enum_dict

def get_trap_severity_display_string(trap_severity_enum_dict, trap_sev_metric_value):
    trap_sev_int_str = str(int(trap_sev_metric_value))
    trap_severity_display_string = trap_sev_int_str
    try:
        trap_severity_display_string = trap_severity_enum_dict[trap_sev_int_str]
    except KeyError:
        pass

    return trap_severity_display_string

def create_trap_data_row_dict(object_name, object_id, child_name, child_id, obj_display_name, timestamp,
                metric_class, agent_name, trapOID, trap_display_name, category, trap_severity, 
                trap_data_dict, additional_data_dict):

    try:
        obj_display_name = trap_data_dict ["Object Name"]
    except KeyError:
        pass
    
    try:
        object_id = trap_data_dict ["Object Id"]
    except KeyError:
        pass
        
    trap_data_row_dict = {
        "object_name" : obj_display_name,
        "timestamp" : timestamp, 
        "category" : metric_class,
        "severity" : trap_severity,
    }
    if (object_id != None and child_id != None):
        trap_data_row_dict ["object_id"] = child_id
        trap_data_row_dict ["parent_object_id"] = object_id
    elif (object_id != None):
        trap_data_row_dict ["object_id"] = object_id

    if (category != None and category != "null"):
        trap_data_row_dict ["trap_category"] = category
    
    trap_data_row_dict ["trap_oid"] = trapOID
    trap_data_row_dict ["trap_display_oid"] = trap_display_name

    try:
        trap_data_row_dict ["violation_name"] = trap_data_dict["Violation Name"]
    except KeyError:
        pass

    try:
        snmp_varbinds = additional_data_dict["SNMP VarBinds"]
        if (snmp_varbinds != None):
            snmp_varbinds_dict = json.loads(snmp_varbinds)
            additional_data_dict["SNMP VarBinds"] = snmp_varbinds_dict
    except:
        pass
    
    # Add additional data to the trap row
    trap_data_row_dict["additional_data"] = additional_data_dict

    return trap_data_row_dict

def process_trap_events_detail(session, base_url, obj_name_id_dict, child_obj_id_name_dict, 
                                    metric_data_resp_dict, metric_class):
    trap_data_by_object_dict = None

    if (metric_data_resp_dict == None):
        return trap_data_by_object_dict

    try:
        element_id_object_info_dict = metric_data_resp_dict["elementIdToObjectInfoMap"]
    except KeyError:
        print("response did not include elementIdToObjectInfoMap")
        return trap_data_by_object_dict


    metric_data_dict = None
    try:
        metric_data_dict = metric_data_resp_dict["metricData"]
    except KeyError:
        print("response did not include metricData")
        
    if (metric_data_dict == None):    
        return trap_data_by_object_dict

    # Get the trap severity enum dict
    trap_severity_enum_dict = get_trap_severity_enum_map(metric_data_dict)
    if (trap_severity_enum_dict == None):
        print("could not find severity enum")
        return trap_data_by_object_dict

    # Get metric field indices
    agent_index = get_metric_field_index(metric_data_dict, "Agent")
    trapOID_index = get_metric_field_index(metric_data_dict, "TrapOID")
    category_index = get_metric_field_index(metric_data_dict, "Category")
    severity_index = get_metric_field_index(metric_data_dict, "Severity")
    trap_display_name_index = get_metric_field_index(metric_data_dict, "TrapDisplayName")
    additional_data_index = get_metric_field_index(metric_data_dict, "AdditionalData")
    data_index = get_metric_field_index(metric_data_dict, "Data")
    if (agent_index == -1 or trapOID_index == -1 or category_index == -1 or severity_index == -1 or
        trap_display_name_index == -1 or data_index == -1 or additional_data_index == -1):
        print("could not find metric field indices")
        return trap_data_by_object_dict

    try:
        metric_element_data_list = metric_data_dict["metricElementDataList"]
    except KeyError:
        print("metric_data_dict did not include metricElementDataList")
        return trap_data_by_object_dict

    # Create a dictionary to hold traps by object
    trap_data_by_object_dict = {}
    for metric_element_data_dict in metric_element_data_list:
        element_id = None
        try:
            element_id = metric_element_data_dict["elementId"]
        except KeyError:
            print("metric_element_data_dict (element: %s) did not include elementId" % (str(metric_element_data_dict)))
            continue

        (object_name, object_id, child_name, child_id, obj_display_name) = get_object_name(
            session, base_url, obj_name_id_dict, child_obj_id_name_dict, element_id_object_info_dict, str(element_id))

        try:
            timestamp_to_values_dict = metric_element_data_dict["timestampToValuesMap"]
        except KeyError:
            print("metric_element_data_dict (element: %s) did not include timestampToValuesMap" % (str(metric_element_data_dict)))
            continue

        try:
            object_trap_list = trap_data_by_object_dict[obj_display_name]
        except KeyError:
            object_trap_list = []
            trap_data_by_object_dict[obj_display_name] = object_trap_list

        for timestamp in timestamp_to_values_dict.keys():
            metric_data_list = timestamp_to_values_dict[timestamp]
            agent_name = metric_data_list[agent_index]
            trapOID = metric_data_list[trapOID_index]
            category = metric_data_list[category_index]
            trap_display_name = metric_data_list[trap_display_name_index]
            trap_severity = get_trap_severity_display_string(trap_severity_enum_dict, metric_data_list[severity_index])

            additional_data_str = metric_data_list[additional_data_index]
            trap_data_str = metric_data_list[data_index]

            additional_data_dict = None
            if (additional_data_str != None):
                additional_data_dict = json.loads(additional_data_str)

            trap_data_dict = None
            if (trap_data_str != None):
                trap_data_dict = json.loads(trap_data_str)

            trap_row_dict = create_trap_data_row_dict(
                object_name, object_id, child_name, child_id, obj_display_name, timestamp,
                metric_class, agent_name, trapOID, trap_display_name, category, trap_severity, trap_data_dict, additional_data_dict
            )

            object_trap_list.append(trap_row_dict)

    return trap_data_by_object_dict

def get_alert_syslog_trap_metric_data(session, base_url, metric_request_data, json_dict, obj_name_id_dict, 
                    child_id_name_dict, alert_profile_name_id_dict):
    # https://localhost:8543/swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data
    metric_url = base_url + "/swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data"
    print(f"\nHTTP POST on URL: {metric_url}")
    for param in metric_request_data.keys():
        param_value = metric_request_data[param]
        print(f"\t{param} : {param_value}")

    resp = session.post(metric_url, verify=False, data=json.dumps(metric_request_data))
    if resp is not None: 
        if resp.status_code >= 200 and resp.status_code < 300:        
            print(f"Status code: {resp.status_code}")
            resp_text = resp.text
            metric_data_resp_dict = json.loads(resp_text)

            metric_class = metric_request_data["metricClass"]
            if (metric_class.endswith("_ALERT_EVENTS_DETAIL")):
                json_dict[metric_class] = process_alert_events_detail(session, base_url, obj_name_id_dict, 
                    child_id_name_dict, metric_data_resp_dict, alert_profile_name_id_dict, metric_class)
            elif (metric_class.endswith("_SYSLOG_EVENTS_DETAIL")):
                json_dict[metric_class] = process_syslog_events_detail(session, base_url, obj_name_id_dict, 
                    child_id_name_dict, metric_data_resp_dict, metric_class)
            elif (metric_class.endswith("_TRAP_EVENTS_DETAIL")):
                json_dict[metric_class] = process_trap_events_detail(session, base_url, obj_name_id_dict, 
                    child_id_name_dict, metric_data_resp_dict, metric_class)
            
            convert_data_additional_data_json_to_dict(metric_data_resp_dict)    
            json_dict[metric_class + " Original Response"] = metric_data_resp_dict
        else:
            print(f"Unable to retrieve resource. Status code: {resp.status_code}")
    else:
        print(f"Unable to retrieve resource from URL: {metric_url}")
    
    return

def get_alert_syslog_trap_from_file(filepath, session, base_url, obj_name_id_dict, child_id_name_dict, alert_profile_name_id_dict):
    multi_metric_dict = {}
    with open(filepath) as f:
        json_content = f.read()
        multi_metric_dict = json.loads(json_content)
        f.close()
    
    json_dict = dict()
    for metric_class in multi_metric_dict.keys():
        metric_data_resp_dict = multi_metric_dict[metric_class]
        if (metric_class.endswith("_ALERT_EVENTS_DETAIL")):
            json_dict[metric_class] = process_alert_events_detail(session, base_url, obj_name_id_dict, 
                child_id_name_dict, metric_data_resp_dict, alert_profile_name_id_dict, metric_class)
        elif (metric_class.endswith("_SYSLOG_EVENTS_DETAIL")):
            json_dict[metric_class] = process_syslog_events_detail(session, base_url, obj_name_id_dict, 
                child_id_name_dict, metric_data_resp_dict, metric_class)
        elif (metric_class.endswith("_TRAP_EVENTS_DETAIL")):
            json_dict[metric_class] = process_trap_events_detail(session, base_url, obj_name_id_dict, 
                child_id_name_dict, metric_data_resp_dict, metric_class)

        convert_data_additional_data_json_to_dict(metric_data_resp_dict)    
        json_dict[metric_class + " Original Response"] = metric_data_resp_dict

    return json_dict

def get_metric_class_object_list_map(metric_class_to_metric_dict, objname_id_map, file_path):
    metric_class_to_obj_list_dict = dict()

    req_objects_list = []
    with open(file_path) as flat_file:
        for line in flat_file:
            if line.startswith("#") or len(line) == 0 or line.isspace():
                continue
            line_list = line.strip().replace('"','').split(',')

            try:
                obj_id = objname_id_map[line_list[0]]
            except KeyError:
                # name could not be mapped to obj id
                print("Could not find id of obj: "+line_list[0]+", ignoring obj")
                continue    
            req_objects_list.append(obj_id)
    
    if (len(req_objects_list) == 0):
        print("No objects specified in input file, using all objects")
        req_objects_list = list(objname_id_map.values())

    for metricClass in metric_class_to_metric_dict:
        metric_class_to_obj_list_dict [metricClass] = req_objects_list

    return metric_class_to_obj_list_dict

def main():
    print("This library contains functions to process data returned by the network metric data REST API")

if __name__ == '__main__':
    main()