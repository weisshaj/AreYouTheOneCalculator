import json
import copy
import datetime
import time
import multiprocessing as mp
from multiprocessing import Queue

import matching_night_calculator
from ayto_functions import fixed_string,percent_string,clear_console,key_is_in_dict, person_is_not_in_pair_list


original_data = None
process_result_dict = {}
system_info_dict = {}
callback_queue = Queue()
start_time = None



def print_results():
    clear_console()
    actual_time = datetime.datetime.now()
    delta_time = actual_time - start_time
    men_dict = original_data["men"]
    women_dict = original_data["women"]

    total_calculations_cnt = 0
    possible_combinations_cnt = 0
    result_pairs = {}


    for process_result in process_result_dict:
        
        process_number = int(process_result)

        result_dict = process_result_dict[process_number]
        if len(result_dict) > 0:
            total_calculations_cnt += result_dict["calculations"]
            possible_combinations_cnt += result_dict["possible_combinations_cnt"]

            for pair in result_dict["pairs"]:
                if key_is_in_dict(pair,result_pairs):
                    result_pairs[pair] += result_dict["pairs"][pair]
                else:
                    result_pairs[pair] = result_dict["pairs"][pair]
    lines = []
    lines.append("Checked  combinations: " + str(total_calculations_cnt))
    lines.append("Possible combinations: " + str(possible_combinations_cnt))
    lines.append("Calculation duration: "  + str(delta_time))
    lines.append("")
    for i in range(len(process_result_dict)):
        if len(process_result_dict[i])>0:
            lines.append("Process: " + str(i) +" Init Pair: " + str(process_result_dict[i]["init_pair_cnt"]) + "/" + str(process_result_dict[i]["max_init_pairs"]) +"  Calculations: " +str(process_result_dict[i]["calculations"])+ "  Possible combinations found: " + str(process_result_dict[i]["possible_combinations_cnt"]))
    lines.append("")

    men_list = []
    women_list = []
    pair_list = []

    for men in men_dict:
        men_name = str(men)
        men_list.append(men_name)
    
    for women in women_dict:
        women_name = str(women)
        women_list.append(women_name)

    for pair in result_pairs:
        pair_name = str(pair)
        pair_list.append(pair_name)


    max_table_entry = "100.00%"
    max_len_table_entry = len(max_table_entry)
    max_len_men = 0
    max_len_women = 0

    for men in men_list:
        men_len = len(men)

        if men_len > max_len_men:
            max_len_men = men_len
    
    if max_len_men < max_len_table_entry:
        max_len_men = max_len_table_entry
    
    

    for women in women_list:
        women_len = len(women)
        if women_len > max_len_women:
            max_len_women = women_len

    if max_len_women < max_len_table_entry:
        max_len_women = max_len_table_entry


    women_line = fixed_string("  ",max_len_men)
    for women in women_list:
        women_line = women_line + "  " + fixed_string(women,max_len_women)

    lines.append(women_line)



    for men in men_list:
        men_line = fixed_string(men,max_len_men)

        for women in women_list:

            pair = men+"+"+women
            
            if pair in pair_list:
                calc_val = round(((result_pairs[pair]/possible_combinations_cnt)*100),2)
                value_string = percent_string(calc_val)
                men_line = men_line + "  " + fixed_string(value_string,max_len_women)
            else:
                men_line = men_line + "  " + fixed_string(" ", max_len_women)

        lines.append(men_line)

    lines.append("")


    for line in lines:
        print(line)
    
    time = datetime.datetime.now()
    date = time.strftime("%Y-%m-%d")
    folder = time.strftime("%Y")
    filename = "./results/"+folder+"/"+season_info+"_"+"result_"+date+".txt"

    f = open(filename, "w")
    for line in lines:
        f.write(line)
        f.write("\n")

def update_values():

    callback_dict = None
    try: 
        callback_dict = callback_queue.get()
    except:
        print("callback_queue.get() error")

    process_number = callback_dict["process_number"]
    process_results = callback_dict["results"]
    process_result_dict[process_number] = process_results
    if callback_queue.empty():
        print_results()
    else:
        update_values()
    
def process_function(data):
    process_number = copy.deepcopy(data[0])
    original_data = copy.deepcopy(data[1])
    initial_pairs = copy.deepcopy(data[2])
    total_possible_pairs = copy.deepcopy(data[3])
    

    mn = matching_night_calculator.matching_night_calculator(original_data["men"],original_data["women"],original_data["perfect_matches"],original_data["no_matches"],original_data["matching_nights"],process_number,callback_queue)
    mn.iterate_combinations(initial_pairs,total_possible_pairs)

    process_results = mn.get_results()
    callback_queue.put(process_results)
    return process_results

def create_seeding_information():
    if multiprocessing_status:
        process_count = mp.cpu_count()
    else:
        process_count = 1
    print("Paralel processes: " +str(process_count))
    system_info_dict["process_count"] = process_count

    men_cnt = len(original_data["men"])
    women_cnt = len(original_data["women"])


    person_dict = {}
    
    for men in original_data["men"]:
        person_dict[men] = original_data["men"][men]
        person_dict[men]["possible_pairs"] = women_cnt            

    for women in original_data["women"]:
        person_dict[women] = original_data["women"][women]
        person_dict[women]["possible_pairs"] = men_cnt

    for pair in original_data["perfect_matches"]:
        men_name,women_name = str(pair).split("+")
        person_dict[men_name]["possible_pairs"] -= 1
        person_dict[women_name]["possible_pairs"] -= 1

    for pair in original_data["no_matches"]:
        men_name,women_name = str(pair).split("+")
        person_dict[men_name]["possible_pairs"] -= 1
        person_dict[women_name]["possible_pairs"] -= 1

    for name in person_dict:
        person_dict[name]["pair_delta"] = person_dict[name]["possible_pairs"] - system_info_dict["process_count"]
    
    #look for a perfect delta
    primary_person = None
    if primary_person == None:    
        for name in person_dict:
            if person_dict[name]["possible_pairs"] == system_info_dict["process_count"]:
                primary_person = str(name)
                break
    
    #look for a highest delta
    if primary_person == None:
        maximum_delta = 0
        maximum_name = None
        for name in person_dict:
            if person_dict[name]["pair_delta"] > maximum_delta:
                maximum_delta = person_dict[name]["pair_delta"]
                maximum_name = str(name)
        primary_person = maximum_name

    total_possible_pairs = []
    for men in original_data["men"]:
        for women in original_data["women"]:
            pair = men + "+" + women
            if pair not in original_data["no_matches"]:

                total_possible_pairs.append(pair)

    pairs_of_primary_person = []
    for pair in total_possible_pairs:
        men_name,women_name = pair.split("+")
        if men_name == primary_person or women_name == primary_person:
            pairs_of_primary_person.append(str(pair))

    possible_pairs = copy.deepcopy(total_possible_pairs)
    for pair in pairs_of_primary_person:
        possible_pairs.remove(pair)

    total_possible_pairs_cnt = len(total_possible_pairs)
    print("Total possible pairs: "+str(total_possible_pairs_cnt))
    system_info_dict["total_possible_pairs_cnt"] = total_possible_pairs_cnt

    pairs_per_process = {}
    for i in range(process_count):
        pairs_per_process[i] = []

    process_number = 0
    while len(pairs_of_primary_person) > 0:
        pair = pairs_of_primary_person[0]
        pairs_per_process[process_number].append(pair)
        pairs_of_primary_person.remove(pair)

        process_number += 1
        if process_number > (process_count - 1):
            process_number = 0 
    
    process_arguments = []
    for i in range(process_count):
        initial_pairs = pairs_per_process[i]

        process_data = (i,original_data,initial_pairs,possible_pairs)
        process_arguments.append(process_data)



    if multiprocessing_status:
        pool = mp.Pool(process_count)
        result_list = pool.map_async(process_function,process_arguments)
        pool.close()
    else:
        process_function(process_arguments[0])

    timer = 5
    while True:
        print(" Update in: "+ str(timer),end="\r")
        time.sleep(1)
        timer -= 1
        
        if timer == 0:
            timer = 5
            if not callback_queue.empty():
            
                update_values()
            if result_list.ready():
                update_values()
                break
        

    print("")
    print("Calculation done")
    print("")
    print_results()

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    

    f = open("settings.json")
    settings = json.load(f)
    season_info = settings["datafile"]
    multiprocessing_status = settings["multiprocessing"]
    f.close()
    data_filename = "./data/"+season_info+".json"

    f = open(data_filename)
    season_data = json.load(f)

    original_data = copy.deepcopy(season_data)
    for perfect_match in original_data["perfect_matches"]:
        men_name,women_name = perfect_match.split("+")

        original_data["men"][men_name]["possible_matches"] -= 1
        if original_data["men"][men_name]["possible_matches"] == 0:
            original_data["men"][men_name]["all_matches_found"] = True
        
        original_data["women"][women_name]["possible_matches"] -= 1
        if original_data["women"][women_name]["possible_matches"] == 0:
            original_data["women"][women_name]["all_matches_found"] = True

    create_seeding_information()

    