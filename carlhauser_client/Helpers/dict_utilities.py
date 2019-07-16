#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List

from common.environment_variable import load_client_logging_conf_file

load_client_logging_conf_file()


def copy_id_to_image(dict_to_modify: Dict) -> Dict:
    '''
    From a dict of pictures/graphe json,
    copy ids of cluster and pictures to their 'picture' attribute
    Useful to have a visjs-classificator readable graph
    :param dict_to_modify: original dictionnary of pictures/clusters/edges ..
    :return: modified and readable by visjs-classificator graph
    '''
    for i in dict_to_modify['clusters']:
        i["image"] = "anchor.png"
        i["shape"] = "icon"
    for i in dict_to_modify['nodes']:
        i["image"] = i["id"]

    return dict_to_modify


def revert_mapping(mapping: Dict) -> Dict:
    '''
    Revert the value/keys of a dictionnary.
    Ex : transform X->Y to Y->X for all values of a dict
    :param mapping: X -> Y dict
    :return: The reversed dict
    '''
    return {v: k for k, v in mapping.items()}


def apply_mapping(dict_to_modify: Dict, mapping: Dict) -> Dict:
    '''
    Modify all occurences in dict_to_modify of keys-values in mapping, by their value
    Ex : {"toto":"tata"}, {"tata":"new"} ==> {"toto":"new"}
    :param dict_to_modify: The original dict
    :param mapping: dict of (values to be replaces) -> (new values)
    :return: the modified dict
    '''
    return update_values_dict(dict_to_modify, {}, mapping)


def apply_revert_mapping(dict_to_modify, mapping_to_revert: Dict):  # -> Dict or List or value ...
    '''
    Revert the value/keys of a dictionnary and apply it to all
    occurences in dict_to_modify of keys-values in mapping, by their value
    Ex : {"toto":"tata"}, {"new":"tata"} ==> {"toto":"new"}
    :param dict_to_modify: The original dict
    :param mapping_to_revert: mapping from name to name, to be reverted before application
    :return: Original dict modified with applied reversed dict
    '''
    reverted_mapping = revert_mapping(mapping_to_revert)
    output_dict = apply_mapping(dict_to_modify, reverted_mapping)
    return output_dict


def update_values_dict(original_dict: Dict, future_dict: Dict, new_mapping: Dict) -> Dict:
    '''
    Recursively updates values of a nested dict by performing recursive calls
    Replace in <original_dict> all keys elements present in <new_mapping> by their value in <new_mapping>
    Ex : {"toto":"tata"}, {"tata":"new"} ==> {"toto":"new"}
    :param original_dict: The original dict
    :param future_dict: The dict were the result will be stored (needed, because recursive calls)
    :param new_mapping: dict of (values to be replaces) -> (new values)
    :return: the modified dict
    '''

    if isinstance(original_dict, Dict):
        # It's a dict
        tmp_dict = {}
        for key, value in original_dict.items():
            tmp_dict[key] = update_values_dict(value, future_dict, new_mapping)
        return tmp_dict
    elif isinstance(original_dict, List):
        # It's a List
        tmp_list = []
        for i in original_dict:
            tmp_list.append(update_values_dict(i, future_dict, new_mapping))
        return tmp_list
    else:
        # It's not a dict, maybe a int, a string, etc. so we replace it with what is needed
        return original_dict if original_dict not in new_mapping else new_mapping[original_dict]


def get_clear_matches(request):
    '''
    Extract a clean list of matches from a request : remove the picture itself from the matches
    :param request: result of a request, a dict
    :return: a clean list of matches (wihtout the picture itself)
    '''

    # We remove the picture "itself" from the matches
    tmp_clean_matches = []

    for match in request.get("list_pictures", []):
        if match["image_id"] != request["request_id"]:
            tmp_clean_matches.append(match)
        # elif match["distance"] != 0:
        #     self.logger.warning(f"Picture {request['request_id']} has not a distance 0 to itself. Strange.")

    return tmp_clean_matches
