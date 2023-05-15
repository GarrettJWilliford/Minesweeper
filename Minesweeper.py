import datetime
import uuid
import random
import pickle
import re
import os
from colorama import Fore, Back, Style


def id_generator(column, row):
    null_value = '0000'
    if column < 10:
        column = '0' + str(column)
    if row < 10:
        row = '0' + str(row)
    return str(column) + str(row)



def generate_mines(bored, mine_count):
    bored_keys = list(bored['bored'].keys())
    mines = []
    for i in range(mine_count):
        mine_key = random.choice(bored_keys)
        bored['bored'][mine_key]['mine'] = True
    return bored



def get_mine_ids(bored):
    mine_keys = []
    for key in bored['bored'].keys():
        if bored['bored'][key]['mine'] == True:
            mine_keys.append(key)
    return mine_keys



def get_color_specs(value):
    return pickle.load(open('minesweeper_color_file.p', 'rb'))[value]

    
def generate_numbers(bored):
    mine_key_list = get_mine_ids(bored)
    key_number_values = {}
    for mine_key in mine_key_list:
        value_list = []
        for column_value in [-1, 0, 1]:
            column_key = mine_key[0:2]
            for row_value in [-1, 0, 1]:
                row_key = mine_key[2:4]
                value_id = id_generator(int(column_key) + (column_value), int(row_key) + (row_value))
                if value_id != mine_key and int(value_id[0:2]) > 0 and int(value_id[2:4]) > 0 \
                and int(value_id[0:2]) <= bored['bored_info']['max_column'] and int(value_id[2:4]) <= bored['bored_info']['max_row']:
                    value_list.append(value_id)
        for value in value_list:
            if value in key_number_values.keys():
                key_number_values[value] += 1
            if value not in key_number_values:
                key_number_values.update({value : 1})
    for key in key_number_values.keys():
        bored['bored'][key]['number'] = key_number_values[key]
    return bored

        

def get_all_object_ids(bored):
    object_id_list = []
    for key in bored['bored'].keys():
        if bored['bored'][key]['number'] != 0 or bored['bored'][key]['mine'] == True:
            object_id_list.append(key)
    return object_id_list



def crawl_space(bored, object_id):
    objects = get_all_object_ids(bored)
    crawled_spaces = []
    for tuple_value in [(-1, 0), (0, -1), (0, 1), (1, 0)]:
        column_id = int(object_id[0:2]) + (tuple_value[0])
        row_id = int(object_id[2:4]) + (tuple_value[1])
        crawl_id = id_generator(column_id, row_id)
        if crawl_id in list(bored['bored'].keys()):
            crawled_spaces.append(crawl_id)
    for tuple_value in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
        column_id = int(object_id[0:2]) + (tuple_value[0])
        row_id = int(object_id[2:4]) + (tuple_value[1])
        crawl_id = id_generator(column_id, row_id)
        if crawl_id in list(bored['bored'].keys()):
            if bored['bored'][crawl_id]['number'] != 0:
                crawled_spaces.append(crawl_id)
    return crawled_spaces



def crawl_spaces(bored, object_id):
    crawled_spaces = []
    active_spaces = crawl_space(bored, object_id)
    for i in range(100):
        if len(active_spaces) == 0:
            break
        current_active_spaces = active_spaces.copy()
        for space in current_active_spaces:
            if space in crawled_spaces:
                active_spaces.remove(space)
                continue
            if bored['bored'][space]['number'] != 0:
                active_spaces.remove(space)
                crawled_spaces.append(space)
            if bored['bored'][space]['number'] == 0:
                active_spaces += crawl_space(bored, space)
                active_spaces.remove(space)
                crawled_spaces.append(space)
    return crawled_spaces
        
    

def select_space(bored, object_id):
    bored['bored'][object_id]['hidden'] = False
    if bored['bored'][object_id]['number'] == 0:
        selected_spaces = crawl_spaces(bored, object_id)
        for space in selected_spaces:
            bored['bored'][space]['hidden'] = False
    return bored




def generate_bored(columns, rows, mines):
    #Add numbers
    #Max 99x99 mines
    bored = {'bored_info' : {'bored_id' : str(uuid.uuid4()), 'date_created' : str(datetime.datetime.now()), 'max_column' : columns, 'max_row' : rows, 'mines' : mines},
             'bored' : {}}
    for column in range(1, columns + 1):
        for row in range(1, rows + 1):
            bored['bored'].update({id_generator(column, row) : {'column' : column, 'row' : row, 'mine' : False, 'hidden' : True, 'flagged' : False, 'number' : 0}})
    bored = generate_numbers(generate_mines(bored, mines))
    return bored




def display_bored(bored, clear_screen = False, game_mode = True):
    if clear_screen:
        null_me = os.system('cls')
    display_line = ''
    column_index = 'MS |'
    for i in range(bored['bored_info']['max_row']):
        cindex = str(i + 1)
        display_line += '----'
        if len(cindex) > 1:
            column_index += ' %s|' % (cindex)
        if len(cindex) == 1:
            column_index += ' %s|' % (('0' + cindex))
    print(column_index)
    display_line += '----'
    number_matrix = {}
    for row in range(1, bored['bored_info']['max_row'] + 1):
        number_matrix.update({row : []})
        row_list = []
        for column in range(1, bored['bored_info']['max_column'] + 1):
            value = bored['bored'][id_generator(column, row)]
            if not game_mode:
                if value['mine'] == True:
                    row_list.append('M')
                if value['mine'] == False:
                    if value['number'] == 0:
                        row_list.append(' ')
                    if value['number'] != 0:
                        row_list.append(value['number'])
            if game_mode:
                if value['flagged'] == True:
                    row_list.append('F')
                if value['hidden'] == True and value['flagged'] == False:
                    row_list.append('?')
                if value['mine'] == True and value['hidden'] == False and value['flagged'] == False:
                    row_list.append('M')
                if value['mine'] == False and value['hidden'] == False and value['flagged'] == False:
                    if value['number'] == 0:
                        row_list.append(' ')
                    if value['number'] != 0:
                        row_list.append(value['number'])
        number_matrix[row] = row_list
    for key in number_matrix.keys():
        print(display_line)
        display_value = str(number_matrix[key])
        display_value = ''.join(display_value)
        row_index = list(number_matrix.keys()).index(key) + 1
        if row_index < 10:
            row_index = '0' + str(row_index)
        if type(row_index) == int:
            row_index = str(row_index)
        formatted_display_string = f"%s | " % (row_index)
        display_value = re.sub("'", '', re.sub(', ', '', display_value))
        display_value = display_value[1:len(display_value) - 1]
        for value in display_value:
            if value in ['1', '2', '3', '4', '5', '6', 'F', 'M', '?']:
                color_spec = get_color_specs(value)
                formatted_display_string += f"{color_spec['color']}{color_spec['brightness']}{value}{Style.RESET_ALL}"
            if value not in ['1', '2', '3', '4', '5', '6', 'F', 'M', '?']:
                formatted_display_string += f"{value}"
            formatted_display_string += f" | "
        print(formatted_display_string)
    print(display_line)




def select_value(bored, object_id):
    bored['bored'][object_id]['hidden'] = False
    return bored




def flag_value(bored, object_id):
    bored['bored'][object_id]['flagged'] = not bored['bored'][object_id]['flagged']
    return bored



def reset_color_file():
    color_file = {
        '?' : {'color' : '\x1b[37m', 'brightness' : '\x1b[2m'},
        'M' : {'color' : '\x1b[31m', 'brightness' : '\x1b[22m'},
        'F' : {'color' : '\x1b[31m', 'brightness' : '\x1b[1m'},
        '1' : {'color' : '\x1b[36m', 'brightness' : '\x1b[22m'},
        '2' : {'color' : '\x1b[36m', 'brightness' : '\x1b[2m'},
        '3' : {'color' : '\x1b[34m', 'brightness' : '\x1b[22m'},
        '4' : {'color' : '\x1b[35m', 'brightness' : '\x1b[1m'},
        '5' : {'color' : '\x1b[33m', 'brightness' : '\x1b[1m'},
        '6' : {'color' : '\x1b[32m', 'brightness' : '\x1b[22m'}}
    pickle.dump(color_file, open('minesweeper_color_file.p', 'wb'))





def get_save_files():
    path = r'/Users/Garrett/Documents/minesweeper_saves/'
    file_list = [] 
    for root, directories, file in os.walk(path):
        for file in file:
            if file[0] != '.':
                file_list.append(os.path.join(file))
    return file_list




def create_new_game(file_name = 'defualt', width = 24, length = 24, mines = 24):
    path = r'/Users/Garrett/Documents/minesweeper_saves/'
    if file_name == 'defualt':
        save_file_list = get_save_files()        
        file_name = 'minesweeper' + str(len(save_file_list))
    pickle.dump(generate_bored(), open(path + file_name + '.p', 'wb'))
    

    


def minesweeper_alpha(columns, rows, mines):
    bored = generate_bored(columns, rows, mines)
    while True:
        display_bored(bored, clear_screen = True)
        command = input('>>| ')
        if command == 'EXIT':
            return
        if command[0] == 'S':
            pickle.dump(bored, open((r'/Users/Garrett/Documents/minesweeper_saves/' + command[1::] + '.p'), 'wb'))
        if command[0] == 'F':
            bored = flag_value(bored, command[1::])
        if command[0] != 'F':
            bored = select_space(bored, command)
        


minesweeper_alpha(10, 10, 10)    
    
