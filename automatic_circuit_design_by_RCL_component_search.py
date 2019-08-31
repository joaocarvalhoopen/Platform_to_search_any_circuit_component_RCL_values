###############################################################################
#                                                                             #
#           Platform to search any circuit component RCL values               #
#                         and tolerance analysis.                             #
#                                                                             #
###############################################################################
# Author:  Joao Nuno Carvalho                                                 #
# Date:    2019.08.30                                                         #
# License: MIT Open Source License                                            #
#                                                                             #
# Description: This is a simple program that is made to be customizable, in   #
#              other words, to be modified to your own specific case. It will #
#              help you in automating the search for the optimal values of    #
# resistors, capacitors and inductors in any circuit that you have a          #
# mathematical description of it. You should also have a clear measure of how #
# to evaluate the error distance regarding what you consider to be the best   #
# result.                                                                     #
# It can also do tolerance analysis.                                          #
# You can customize the program in five simple steps, that are documented in  #
# code.                                                                       #
#                                                                             #
# The inputs are:                                                             #
#     dict_input_fixed_parameters ex:{VCC, VEE, GND},                         #
#     dict_resistors ex:{R1 [100, 100000, 1%], R2 [1000, 10000, 5%]},         #
#     dict_capacitors ex:{C1 [1e-6, 4.7e-6, 10e-6, 10%], C2 [],},             #
#     dict_inductors ex:{L1 [1e-3, 5e-3, 10e-3, 10%], L2 [],},                #
#     dict_target_calc_values ex:{V_low_threshold, V_high_threshold}          #
#                                                                             #
# How it works?                                                               #
# It works by making the full search of all combinations of values of         #
# components, to identify the ones that produce the smallest error. In this   #
# way it speeds up immensely the manual experimentation while dimensioning.   #
# The resistors are from the E24 scale and the tolerance can be chosen from   #
# 5%, 1%, 0.1% or 0.01%. The capacitors are from E12 scale. Or you can choose #
# specific values or sets of values for each component.                       #
# Don't forget that there is a combinatorial explosion in the total number of #
# values that can be evaluated, but even with this simple version I hope that #
# it could be useful. Other approaches to this problem of searching for an    #
# optimal configuration of passive components exists, and maybe in the future #
# I will implement a version based on Genetic Algorithms to expand the        #
# current work to more simultaneous components.                               #
# Before you start, please always do a schematic diagram to better understand #
# the program you need to write.                                              #
#                                                                             #
# Note: The program comes with an example of implementation that I used while #
#       developing and that will help to take any dought on how to customize  #
#       it. The example implements in this new platform the some circuit that #
#       is calculated and documented in the project [Design Asymmetrical      #
#       Inverted Schmitt-Trigger Single Supply program](https://github.com/   #
#       joaocarvalhoopen/Design_Asymmetrical_Inverted_Schmitt_Trigger_Single_ #
#       Supply_program).                                                      #
###############################################################################

# Imports
import math
import itertools
import time

##########
# Constants for dictionary entries.

# In Fixed Parameters.
class InFixP:
    C_NAME        = "name"
    C_VALUE       = "value"
    C_UNITS       = "units"
    C_DESCRIPTION = "description"

# Components R, C and L    
class Comp:
    C_NAME        = "name"
    C_VALUE       = "value"
    C_VALUE_SET   = "value_set"
    C_VALUE_SCALE = "value_scale"
    C_TOLERANCE   = "tolerance"
    C_DESCRIPTION = "description"
    # Internal.
    C_CURR_VALUE  = "curr_value"
    C_BEST_VALUE  = "best_value"
    C_WORST_VALUE = "worst_value"
    C_EXPANDED_VALUES    = "expanded_values"
    C_EXPANDED_TOLERANCE = "expanded_tolerance" 

# Target calc values.
class TCalcValues: 
    C_NAME         = "name"
    C_TARGET_VALUE = "target_value"
    C_UNITS        = "units"
    C_DESCRIPTION  = "description"
    # Internal.
    C_CALC_VALUE   = "calc_value"
    C_BEST_VALUE   = "best_value"
    C_WORST_VALUE  = "worst_value"

######################################################################
######################################################################
#                                                                    # 
#  START OF CUSTOMIZING:                                             #
#  Begining of section in the source code that has to be customized  #
#  to your specific case.                                            #
#                                                                    #
######################################################################

#######
# Step 1 - Please fill the following program configuration dictionaries
#          to your specification, follow your schematic diagram.

# Note: The scales of the resistor values so that an OpAmp circuit is stable,
# normally are between 1K and 100K, but I use a extended version from
# 100 Ohms to 1MOhms.
# scales = [100, 1000, 10000, 100000]

dic_in_fix_param = {"VCC": {InFixP.C_NAME : "VCC",
                            InFixP.C_VALUE : 5.0,
                            InFixP.C_UNITS : "Volt",
                            InFixP.C_DESCRIPTION : "Positive supply reference voltage." },
                    
                    "GND": {InFixP.C_NAME : "GND",
                            InFixP.C_VALUE : 0.0,
                            InFixP.C_UNITS : "Volt",
                            InFixP.C_DESCRIPTION : "Ground reference voltage." } }

dic_resistors = { "R1": {Comp.C_NAME : "R1",
                         Comp.C_VALUE : None,
                         Comp.C_VALUE_SET : None, #[100, 200],
                         Comp.C_VALUE_SCALE : [100, 1000, 10000, 100000],
                         Comp.C_TOLERANCE : 1.0, 
                         Comp.C_DESCRIPTION : "Upper resistor of voltage divider.",
                         # Internal
                         Comp.C_CURR_VALUE  : None,
                         Comp.C_BEST_VALUE  : None, 
                         Comp.C_WORST_VALUE : None },

                  "R2": {Comp.C_NAME : "R2",
                         Comp.C_VALUE : None,
                         Comp.C_VALUE_SET : None,   # [100],
                         Comp.C_VALUE_SCALE : [100, 1000, 10000, 100000],
                         Comp.C_TOLERANCE : 1.0,
                         Comp.C_DESCRIPTION : "Lower resistor of voltage divider.",
                         # Internal
                         Comp.C_CURR_VALUE  : None,
                         Comp.C_BEST_VALUE  : None, 
                         Comp.C_WORST_VALUE : None },

                  "R3": {Comp.C_NAME : "R3",
                         Comp.C_VALUE : None,
                         Comp.C_VALUE_SET : None,   # [100],
                         Comp.C_VALUE_SCALE : [100, 1000, 10000, 100000],
                         Comp.C_TOLERANCE : 1.0,
                         Comp.C_DESCRIPTION : "OpAmp feedback resistor.",
                         # Internal
                         Comp.C_CURR_VALUE  : None,
                         Comp.C_BEST_VALUE  : None, 
                         Comp.C_WORST_VALUE : None } }
                                             
dic_capacitors = { "C1": {Comp.C_NAME : "C1",
                         Comp.C_VALUE : 1e-6,
                         Comp.C_VALUE_SET : None,
                         Comp.C_VALUE_SCALE : None, # [1e-9], # [1e-9, 1e-8], # 1nF e 10nF x E12  # None,  
                         Comp.C_TOLERANCE : 10.0, 
                         Comp.C_DESCRIPTION : "Not used capacitor.",
                         # Internal
                         Comp.C_CURR_VALUE  : None,
                         Comp.C_BEST_VALUE  : None, 
                         Comp.C_WORST_VALUE : None },

                   "C2": {Comp.C_NAME : "C2",
                         Comp.C_VALUE : None,
                         Comp.C_VALUE_SET : [1e-6, 10e-6],
                         Comp.C_VALUE_SCALE : None,
                         Comp.C_TOLERANCE : 1.0,
                         Comp.C_DESCRIPTION : "Not used capacitor.",
                         # Internal
                         Comp.C_CURR_VALUE  : None,
                         Comp.C_BEST_VALUE  : None, 
                         Comp.C_WORST_VALUE : None  } }
                
dic_inductors = { "L1": {Comp.C_NAME : "L1",
                         Comp.C_VALUE : 1e-3,
                         Comp.C_VALUE_SET : None,
                         Comp.C_VALUE_SCALE : None,
                         Comp.C_TOLERANCE : 20.0, 
                         Comp.C_DESCRIPTION : "Not used inductor.",
                         # Internal
                         Comp.C_CURR_VALUE  : None,
                         Comp.C_BEST_VALUE  : None, 
                         Comp.C_WORST_VALUE : None } }

dic_target_calc_values = {"V_low_threshold": {TCalcValues.C_NAME : "V_low_threshold",
                                              TCalcValues.C_TARGET_VALUE : 0.555,
                                              TCalcValues.C_UNITS : "Volt",
                                              TCalcValues.C_DESCRIPTION : "The threshold for the lower voltage.",
                                              # Internal
                                              TCalcValues.C_CALC_VALUE : None,
                                              TCalcValues.C_BEST_VALUE : None,
                                              TCalcValues.C_WORST_VALUE : None },

                          "V_high_threshold": {TCalcValues.C_NAME : "V_high_threshold",
                                               TCalcValues.C_TARGET_VALUE : 0.575,
                                               TCalcValues.C_UNITS : "Volt",
                                               TCalcValues.C_DESCRIPTION : "The threshold for the higher voltage.",
                                               # Internal
                                               TCalcValues.C_CALC_VALUE : None,
                                               TCalcValues.C_BEST_VALUE : None,
                                               TCalcValues.C_WORST_VALUE : None } }


#######
# Step 2 - Optional - Write the function that will test the consistency of
#          the fixed parameters.

def consistency_testing_of_fixed_parameters():
    VCC = get_dic_in_fix_param("VCC", "value") 
    
    V_low_threshold_target  = get_dic_target_calc_values("V_low_threshold", TCalcValues.C_TARGET_VALUE) 
    V_high_threshold_target = get_dic_target_calc_values("V_high_threshold", TCalcValues.C_TARGET_VALUE)

    passed_tests = True
    if  not ( 0 < VCC):
        print("Error in specification VCC, it has to be: 0 < VCC")
        passed_tests = False
    if  not (V_low_threshold_target < V_high_threshold_target):
        print("Error in specification, it has to be: V_low_threshold_target < V_high_threshold_target")
        passed_tests = False   
    if  not (0 <= V_low_threshold_target <= VCC):
        print("Error in specification, it has to be: 0 <= V_low_threshold_target <= VCC")
        passed_tests = False
    if  not (0 <= V_high_threshold_target <= VCC):
        print("Error in specification, it has to be: 0 <= V_high_threshold_target <= VCC")
        passed_tests = False
    return passed_tests


#######
# Step 3 - Please write the function to calc the equations of your circuit
#          that will use one combination of values in it's evaluation.

def calc_evaluation_of_circuit_equations():
    # Get the values of the fix parameters and of the current combination of components
    # from all dictionries.
    # "curr_value" is dict entry that is dynamically added.
    VCC = get_dic_in_fix_param("VCC", InFixP.C_VALUE)
    R1  = get_dic_resistors("R1", Comp.C_CURR_VALUE)
    R2  = get_dic_resistors("R2", Comp.C_CURR_VALUE)
    R3  = get_dic_resistors("R3", Comp.C_CURR_VALUE)
    C1  = get_dic_capacitors("C1", Comp.C_CURR_VALUE)
    C2  = get_dic_capacitors("C2", Comp.C_CURR_VALUE)
    L1  = get_dic_inductors("L1", Comp.C_CURR_VALUE)

    # print("R1: ", R1)
    # print("R2: ", R2)
    # print("R3: ", R3)
    # print("C1:", C1)
    # print("C2:", C2)
    # print("L1:", L1)

    V_low_threshold  = 0.0
    V_high_threshold = 0.0

    # Calc V_low_threshold.
    R_total_low = (R2 * R3) / float((R2 + R3))
    V_low_threshold = VCC * R_total_low / float((R1 + R_total_low)) 

    # Calc V_high_threshold.
    R_total_high = (R1 * R3) / float((R1 + R3))
    V_high_threshold = VCC * R2 / float((R2 + R_total_high)) 

    # Write the calculated values in the dictionary of the target values.
    set_dic_target_calc_values("V_low_threshold", TCalcValues.C_CALC_VALUE, V_low_threshold)
    set_dic_target_calc_values("V_high_threshold", TCalcValues.C_CALC_VALUE, V_high_threshold)


#######
# Step 4 - Please write the function to calc the distance error from the
#          intended dict_target_calc_values of the evaluation of one
#          combination of values. To evaluate the best combination.

def calc_distance_error_best():
    best_prev_error = get_best_prev_error() 
    V_low_threshold_target  = get_dic_target_calc_values("V_low_threshold",  TCalcValues.C_TARGET_VALUE)
    V_high_threshold_target = get_dic_target_calc_values("V_high_threshold", TCalcValues.C_TARGET_VALUE)
    V_low_threshold_obtained  = get_dic_target_calc_values("V_low_threshold",  TCalcValues.C_CALC_VALUE)
    V_high_threshold_obtained = get_dic_target_calc_values("V_high_threshold", TCalcValues.C_CALC_VALUE)    
    
    better_combination_values = False
    current_error = math.sqrt( math.pow(V_low_threshold_target - V_low_threshold_obtained, 2) + 
                     math.pow(V_high_threshold_target - V_high_threshold_obtained, 2) )
    
    if current_error < best_prev_error:
        better_combination_values = True
        set_best_prev_error(current_error)
        set_dic_target_calc_values("V_low_threshold",  TCalcValues.C_BEST_VALUE, V_low_threshold_obtained)
        set_dic_target_calc_values("V_high_threshold", TCalcValues.C_BEST_VALUE, V_high_threshold_obtained)    

    return better_combination_values


#######
# Step 5 - Please write the function to calc the absolute distance error from
#          the intended dict_target_calc_values of the evaluation of one
#          combination of values for the worst case, bigger error.
#          To evaluate the max tolerance.

def calc_absolute_distance_error_worst():
    worst_prev_error = get_worst_prev_error() 
    V_low_threshold_target  = get_dic_target_calc_values("V_low_threshold",  TCalcValues.C_TARGET_VALUE)
    V_high_threshold_target = get_dic_target_calc_values("V_high_threshold", TCalcValues.C_TARGET_VALUE)
    V_low_threshold_obtained  = get_dic_target_calc_values("V_low_threshold",  TCalcValues.C_CALC_VALUE)
    V_high_threshold_obtained = get_dic_target_calc_values("V_high_threshold", TCalcValues.C_CALC_VALUE)    

    even_worst_combination_values = False
    current_error = (math.fabs(V_low_threshold_target - V_low_threshold_obtained) 
            + math.fabs(V_high_threshold_target - V_high_threshold_obtained)) 
    if current_error > worst_prev_error:
        even_worst_combination_values = True
        set_worst_prev_error(current_error)
        set_dic_target_calc_values("V_low_threshold",  TCalcValues.C_WORST_VALUE, V_low_threshold_obtained)
        set_dic_target_calc_values("V_high_threshold", TCalcValues.C_WORST_VALUE, V_high_threshold_obtained)    

    return even_worst_combination_values


#################################################################
#                                                               # 
#  END OF CUSTOMIZING:                                          #
#  End of section in the source code that has to be customized  #
#  to your specific case.                                       #
#                                                               #
#################################################################
#################################################################

# E24 Standard resistor series.
E24_resistor_values = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2,
                       2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
                       5.6, 6.2, 6.8, 7.5, 8.2, 9.1]

E12_capacitor_values = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7,
                        5.6, 6.8, 8.2]

# Global best previous error.
g_best_prev_error = 10000000000.0

# Global worst previous error.
g_worst_prev_error = 0.0


def get_best_prev_error():
    return g_best_prev_error

def set_best_prev_error(best_prev_error):
    global g_best_prev_error 
    g_best_prev_error = best_prev_error

def get_worst_prev_error():
    return g_worst_prev_error

def set_worst_prev_error(worst_prev_error):
    global g_worst_prev_error 
    g_worst_prev_error = worst_prev_error

def process_inner_dic(inner_dic, field, dictionary):
    if inner_dic != None:
        val = inner_dic.get(field)
        if val != None:
            return val
        else:
            raise ValueError("Error ", field, " not in the dictionary!")    
    else:
        raise ValueError("Error ", id, " not in the ", dictionary, "!")

def get_dic_in_fix_param(id, field):
    inner_dic = dic_in_fix_param.get(id)
    return process_inner_dic(inner_dic, field, dic_in_fix_param)

def get_dic_resistors(id, field):
    inner_dic = dic_resistors.get(id)
    return process_inner_dic(inner_dic, field, dic_resistors)

def get_dic_capacitors(id, field):
    inner_dic = dic_capacitors.get(id)
    return process_inner_dic(inner_dic, field, dic_capacitors)

def get_dic_inductors(id, field):
    inner_dic = dic_inductors.get(id)
    return process_inner_dic(inner_dic, field, dic_inductors)

def get_dic_target_calc_values(id, field):
    inner_dic = dic_target_calc_values.get(id)
    return process_inner_dic(inner_dic, field, dic_target_calc_values)

# Write the calculated values in the dictionary of the target values.
def set_dic_target_calc_values(id, field, value):
    inner_dic = dic_target_calc_values.get(id)
    if inner_dic != None:
        inner_dic[field] = value
    else:
        raise ValueError("Error ", id, " not a valid target_calc_value id!")

def expand_component(component_dic, standard_scale_values):
    for _, component in component_dic.items():
        values_list = []
        value = component.get(Comp.C_VALUE)
        if value == None:
            values = component.get(Comp.C_VALUE_SET)
            if values == None:
                values_scale = component.get(Comp.C_VALUE_SCALE)
                values_list = []
                for scale in values_scale:
                    for val in standard_scale_values:
                        value = val * scale 
                        values_list.append(value)
            else:
                values_list = values
        else:
            values_list = [value] 
        component[Comp.C_EXPANDED_VALUES] = values_list         

# Called for the 3 types of components, R, C and L.   
def make_list_component_expanded_values(dic_component, field_of_expansion_values_or_tolerance):
    list_component = []    
    for _, compone in dic_component.items(): 
        list_component.append( (compone.get(Comp.C_NAME), compone.get(field_of_expansion_values_or_tolerance)) )
    list_component.sort()
    return list_component

def make_two_combined_list_of_components(list_resistors, list_capacitors, list_inductors):
    list_components_ids = []
    list_components_list_values = []
    for id, list_val in list_resistors:
        list_components_ids.append(id)
        list_components_list_values.append(list_val)
    for id, list_val in list_capacitors:
        list_components_ids.append(id)
        list_components_list_values.append(list_val)
    for id, list_val in list_inductors:
        list_components_ids.append(id)
        list_components_list_values.append(list_val)
    return (list_components_ids, list_components_list_values)

def map_ids_and_component_combination_vals__set_fields(list_components_ids, combination, field):
    for id, val in zip(list_components_ids, combination):
        if id.startswith('R'):
            dic_resistors[id][field] = val
        elif id.startswith('C'):
            dic_capacitors[id][field] = val
        elif id.startswith('L'):
            dic_inductors[id][field] = val
        else:
            raise ValueError("Error ", id, " not a valid in combinatorial processing!")

def full_search_of_R_C_L_component_values():
    # We get all the dict for each component, and in it all the expanded_values lists and sort by id.
    list_resistors  = make_list_component_expanded_values(dic_resistors,  Comp.C_EXPANDED_VALUES)
    list_capacitors = make_list_component_expanded_values(dic_capacitors, Comp.C_EXPANDED_VALUES)    
    list_inductors  = make_list_component_expanded_values(dic_inductors,  Comp.C_EXPANDED_VALUES)    

    # We are going to make two lists, one for ids and the other for expanded_list_value to apply
    # the cartesian product. Generating all combinations of element in each list as a "product".
    # Like for oa A of for of B of for of C..... for n lists. 
    res = make_two_combined_list_of_components(list_resistors, list_capacitors, list_inductors) 
    list_components_ids, list_components_list_values = res
    
    # Calc max number of evaluation evaluations, we have to multiply all sub-list lengths.
    max_number_evaluations = 1
    for lst in list_components_list_values:
        length = len(lst)
        max_number_evaluations = max_number_evaluations * length

    five_perc = int(max_number_evaluations / 20.0)

    if max_number_evaluations > 25000000:
        print("Number of combnations:", max_number_evaluations, "  5%: ", five_perc)
        flag = True
        while(flag):
            msg = "ALERT: Can take a long time to process, max_number_evaluations = " + str(max_number_evaluations) + \
                  " safe[< 25.000.000], continue (y, n)? "
            resp = input(msg)
            if (resp == "y") or (resp == "Y"):
                break
            elif (resp == "n") or (resp == "N"):
                # Terminates the program.
                exit()

    # Cartesian product between list elements that ares list.
    iter_combinations = itertools.product(*list_components_list_values)

    print("Number of combnations:", max_number_evaluations, "  5%: ", five_perc)
    
    start_time = time.time()
    index = 0
    for combination in iter_combinations:
        if index == 1000:
            end_time = time.time()
            total_seconds = (end_time - start_time) * max_number_evaluations / 1000.0
            hours   = math.floor(total_seconds / 3600.0)
            minuts  = math.floor((total_seconds - (hours * 3600)) / 60.0)  
            seconds = total_seconds - (hours*3600) - (minuts* 60)
            print("Estimated time: %d H %d M %d S " % (hours, minuts, seconds) )
            print("Progress: ", end='')
            print("||", end='', flush=True)

        if index > 1001:
            if  index % (five_perc*10)  == 0:
                print("|", end='', flush=True)
            if  index % (five_perc*5)  == 0:
                print("|", end='', flush=True)
            elif  index % five_perc == 0:
                print(".", end='', flush=True)
        index += 1 

        # Set the components fields for the C_CURR_VALUE.
        map_ids_and_component_combination_vals__set_fields(list_components_ids, combination, Comp.C_CURR_VALUE)
                
        # Evaluate the equations of the circuit for the current combinations of components.    
        calc_evaluation_of_circuit_equations()
        
        # Calculate the error distance for the current evaluation to the target values.
        better_combination_values = calc_distance_error_best()
        if better_combination_values == True:
            # Set the components fields for the C_BEST_VALUE.
            map_ids_and_component_combination_vals__set_fields(list_components_ids, combination, Comp.C_BEST_VALUE)

    print("\n")

def expand_each_component_tolerance(comp_val, comp_tolerance_perc):
    comp_value_list = []
    delta = comp_val * comp_tolerance_perc * 0.01
    comp_value_list.append(comp_val - delta)
    comp_value_list.append(comp_val)
    comp_value_list.append(comp_val + delta)
    return comp_value_list

def expand_component_tolerance_value_list(dic_component):
    for _, compone in dic_component.items():
        comp_best_value     = compone.get(Comp.C_BEST_VALUE)
        comp_tolerance_perc = compone.get(Comp.C_TOLERANCE)
        expanded_tolerance_list = expand_each_component_tolerance(comp_best_value, comp_tolerance_perc)
        compone[Comp.C_EXPANDED_TOLERANCE] = expanded_tolerance_list

def worst_tolerance_component_analysis():
    # Adds the extremes and the center value.
    expand_component_tolerance_value_list(dic_resistors)
    expand_component_tolerance_value_list(dic_capacitors)
    expand_component_tolerance_value_list(dic_inductors)

    # We get all the dict for each component, and in it all the expanded_values lists and sort by id.
    list_resistors  = make_list_component_expanded_values(dic_resistors,  Comp.C_EXPANDED_TOLERANCE)
    list_capacitors = make_list_component_expanded_values(dic_capacitors, Comp.C_EXPANDED_TOLERANCE)    
    list_inductors  = make_list_component_expanded_values(dic_inductors,  Comp.C_EXPANDED_TOLERANCE)    

    # We are going to make two lists, one for ids and the other for expanded_list_value to apply
    # the cartesian product. Generating all combinations of element in each list as a "product".
    # Like for oa A of for of B of for of C..... for n lists. 
    res = make_two_combined_list_of_components(list_resistors, list_capacitors, list_inductors) 
    list_components_ids, list_components_list_values = res

    # Cartesian product between list elements that ares list.
    iter_combinations = itertools.product(*list_components_list_values)

    for combination in iter_combinations:

        # Set the components fields for the C_CURR_VALUE.
        map_ids_and_component_combination_vals__set_fields(list_components_ids, combination, Comp.C_CURR_VALUE)
                
        # Evaluate the equations of the circuit for the current combinations of components.    
        calc_evaluation_of_circuit_equations()
        
        # Calculate the error distance for the current evaluation to the target values.
        even_worst_combination_values = calc_absolute_distance_error_worst()
        if even_worst_combination_values == True:
            # Set the components fields for the C_WORST_VALUE.
            map_ids_and_component_combination_vals__set_fields(list_components_ids, combination, Comp.C_WORST_VALUE)

def main():
    print("#####################################################")
    print("#                                                   #")
    print("#  Platform to search any circuit component values  #")
    print("#             and tolerance analysis.               #")
    print("#                                                   #")
    print("#####################################################")
    print("")
    
    print("### Specification:")
    
    print("Fixed parameters.")
    for _, fix_param in dic_in_fix_param.items():
        print("%s: %f %s" % (fix_param.get(InFixP.C_NAME), fix_param.get(InFixP.C_VALUE), fix_param.get(InFixP.C_UNITS)) )
    print("")
    
    print("Target calculation values.")
    for _, target_values in dic_target_calc_values.items():
        print("%s_target: %f %s" % (target_values.get(TCalcValues.C_NAME), target_values.get(TCalcValues.C_TARGET_VALUE),
                                    target_values.get(TCalcValues.C_UNITS)) )
    print("")

    passed_tests = consistency_testing_of_fixed_parameters()
    if passed_tests == False:
        return

    # Expand the resitors.
    expand_component(dic_resistors, E24_resistor_values)
    # Expand the capacitors.
    expand_component(dic_capacitors, E12_capacitor_values)
    # Expand the inductors.
    expand_component(dic_inductors, None)

    # Makes all the combinatorics of component values.
    # Iterate through each combination.
    #     Evaluate each.
    #     Calculate the distance Error.
    #     Keep the best one. 
    full_search_of_R_C_L_component_values()

    print("### Solution")
    print("Best_error: ", get_best_prev_error())

    print("Obtained calculation values.")
    for _, target_values in dic_target_calc_values.items():
        print("%s_obtained: %f %s  delta: %s %s" % (target_values.get(TCalcValues.C_NAME),
              target_values.get(TCalcValues.C_BEST_VALUE), target_values.get(TCalcValues.C_UNITS), 
              math.fabs(target_values.get(TCalcValues.C_TARGET_VALUE) - target_values.get(TCalcValues.C_BEST_VALUE)),
              target_values.get(TCalcValues.C_UNITS)) )
    print("")

    print("Best resistor values.")
    for _, R in dic_resistors.items():
        print("Best %s: %f Ohms %f %%" % (R.get(Comp.C_NAME), R.get(Comp.C_BEST_VALUE), R.get(Comp.C_TOLERANCE)) )
    print("")

    print("Best capacitor values.")
    for _, C in dic_capacitors.items():
        print("Best %s: %f Farads %f %%" % (C.get(Comp.C_NAME), C.get(Comp.C_BEST_VALUE), C.get(Comp.C_TOLERANCE)) )
    print("")

    print("Best inductor values.")
    for _, L in dic_inductors.items():
        print("Best %s: %f Henry's %f %%" % (L.get(Comp.C_NAME), L.get(Comp.C_BEST_VALUE), L.get(Comp.C_TOLERANCE)) )
    print("")

    ## Tolerance components analysis R, C and L.
    worst_tolerance_component_analysis()
    
    print("### Resistor tolerance analysis")
    print("Worst_error: ", get_worst_prev_error)
    for _, target_values in dic_target_calc_values.items():
        print("Worst %s_obtained: %f %s  delta: %s %s" % (target_values.get(TCalcValues.C_NAME),
              target_values.get(TCalcValues.C_WORST_VALUE), target_values.get(TCalcValues.C_UNITS), 
              math.fabs(target_values.get(TCalcValues.C_TARGET_VALUE) - target_values.get(TCalcValues.C_WORST_VALUE)),
              target_values.get(TCalcValues.C_UNITS)) )
    print("")

    print("Worst resistor values.")
    for _, R in dic_resistors.items():
        print("Worst %s: %f Ohms %f %%" % (R.get(Comp.C_NAME), R.get(Comp.C_WORST_VALUE), R.get(Comp.C_TOLERANCE)) )
    print("")

    print("Worst capacitor values.")
    for _, C in dic_capacitors.items():
        print("Worst %s: %f Farads %f %%" % (C.get(Comp.C_NAME), C.get(Comp.C_WORST_VALUE), C.get(Comp.C_TOLERANCE)) )
    print("")

    print("Worst inductor values.")
    for _, L in dic_inductors.items():
        print("Worst %s: %f Henry's %f %%" % (L.get(Comp.C_NAME), L.get(Comp.C_WORST_VALUE), L.get(Comp.C_TOLERANCE)) )


if __name__ == "__main__":
    main()


