import os
import json
import copy


def load_settings():
    f = open("settings.json")
    settings = json.load(f)
    f.close()
    return settings

def load_season_data(season_data_name):
    filename_full = "./data/"+season_data_name+".json"
    f = open(filename_full)
    season_data = json.load(f)
    f.close()
    return season_data

def write_server_data(server_data):
    f = open("./cache/server_data.txt", "w")
    json_file = json.dumps(server_data)
    f.write(json_file)
    f.close()

def load_server_data():
    f = open("./cache/server_data.txt", "r")
    data_str = f.read()
    json_data = json.loads(data_str)
    f.close()
    return json_data

def load_result_data():
    f = open("./cache/result_data.txt", "r")
    data_str = f.read()
    json_data = json.loads(data_str)
    f.close()
    return json_data

def write_result_data(result_data):
    f = open("./cache/result_data.txt", "w")
    json_file = json.dumps(result_data)
    f.write(json_file)
    f.close()

def get_calculation_data():
    f = open("./cache/server_data.txt", "r")
    data_str = f.read()
    json_data = json.loads(data_str)
    f.close()

    calculation_data = {
        "finished":False
    }
    if len(json_data["seeding_pairs"]) == 0:
        calculation_data["finished"] = True
    else:
        request_counter = json_data["request_counter"]
        seeding_combination = json_data["seeding_pairs"][request_counter]
        
        calculation_data["seeding_combination"] = seeding_combination
        request_counter += 1
        if request_counter >= len(json_data["seeding_pairs"]):
            request_counter = 0
    
        json_data["request_counter"] = request_counter

        write_server_data(json_data)
        
    return calculation_data

def remove_person_from_person_list(person_name_input,person_list_input):
    person_list = []
    for person_name in person_list_input:
        if person_name != person_name_input:
            person_list.append(person_name)
    return person_list    
    
def get_total_possible_pairs(season_data):
    total_possible_pairs = []
    for men in season_data["men"]:
        for women in season_data["women"]:
            pair = men + "+" + women
            if pair not in season_data["no_matches"]:

                total_possible_pairs.append(pair)
    return total_possible_pairs

def no_double_names_in_pair_combination(pair_combination):
    includet_men = []
    includet_women = []
    for pair in pair_combination:

        men,women = pair.split("+")
        if men not in includet_men:
            includet_men.append(men)
        else:
            return False

        if women not in includet_women:
            includet_women.append(women)
        else:
            return False
    
    return True

def print_list(list):
    for entry in list:
        print(entry,end=" ")
    print("")

def pair_is_in_pair_list(input_pair, input_pair_list):
        for pair_entry in input_pair_list:
            if pair_entry == input_pair:
                return True
        return False

def one_of_pair_is_in_pair_list(input_pair,input_pair_list):
    input_pair_men,input_pair_women = input_pair.split("+")
    for pair in input_pair_list:
        pair_men,pair_women = pair.split("+")
        if (pair_men == input_pair_men) and (pair_women == input_pair_women):
            return True

    return False

def remove_each_of_pair_from_pair_list(input_pair,input_pair_list):
    input_pair_men,input_pair_women = input_pair.split("+")
    return_pair_list=[]
    for pair in input_pair_list:
        pair_men,pair_women = pair.split("+")
        if (pair_men != input_pair_men) and (pair_women != input_pair_women):
            return_pair_list.append(pair)

    return return_pair_list

def person_is_not_in_pair_list(input_person,input_pair_list):
    for pair in input_pair_list:
        pair_men,pair_women = pair.split("+")
        if pair_men == input_person or pair_women == input_person:
            return False

    return True

def alter_string(spaces_before,input_string,spaces_after):
    return spaces_before + input_string + spaces_after

def fixed_string(input_string,lenght):
    in_str = input_string
    while len(in_str) < lenght:
        in_str = " " + in_str
    return in_str

def pair_is_in_pair_list(input_pair, input_pair_list):
    for pair_entry in input_pair_list:
        if pair_entry == input_pair:
            return True
    return False

def key_is_in_dict(input_key,input_dict):
        for key in input_dict:
            if key == input_key:
                return True
        return False 

def print_table(men_dict,women_dict,pair_dict,process_result_dict):
    pass

def percent_string(double_val):
    result = str(double_val)

    pre,after = result.split(".")
    if len(after) < 2:
        after = after + "0"
    
    result = pre+","+after+" %"
    return result

def clear_console():
    if os.name in ('nt', 'dos'): 
        os.system('cls')
    else:
        os.system('clear')