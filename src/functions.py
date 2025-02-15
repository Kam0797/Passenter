from datetime import datetime
import os
import subprocess
import sys
from pathlib import Path
from getpass import getpass

import filetype
from openpyxl import Workbook

# for extract_range() --bug?
temp_word = ''
word_start = False

def is_pdf(path):
    try:
        mime = filetype.guess(path).mime 
        if  mime == 'application/pdf':
            return True
    except Exception  as e:
        print('\tError:',e)
    return False

def get_merge_choice(merge_choice):
    # print('mer',len(merge_choice),'f')
    if merge_choice == 'y' or merge_choice == 'Y':
        return True
    elif len(merge_choice) > 1:
        print("I think you may have mistaken... \ntype y if the header has stacked words \nN - not stacked is the default")
        merge_choice = input("Does the header row have stacked words? (y/N):")
        get_merge_choice(merge_choice)
    return False


def extract_range(data,line_start_index,iter,end,destin):
    global temp_word
    global word_start

    
    if data[iter] != ' ' or data[iter] == ' ' and data[iter] != ' ' and data[iter-1] != ' ': # just dont know how this actually works :(
            temp_word+=data[iter]
            # print('tt',iter,temp_word) //for debug

            if word_start == False:
                destin[1].append(iter-line_start_index)
                word_start = not word_start

    if (data[iter] == ' ' and data[iter+1] == ' ') or data[iter+1] == '\n':
            if temp_word != '' :
                if data[iter+1] == '\n':
                    destin[2].append(iter+1-line_start_index)
                else:
                    destin[2].append(iter-line_start_index)
                destin[0].append(temp_word)
                word_start = not word_start
                temp_word=''
            elif end is not None and iter == end-1 and temp_word == '' :
                destin[0].append(f'#None{end}')#1 2067
                destin[1].append(f'#None{end}')
                destin[2].append(f'#None{end}')

def incr_xy(x,y):
    if x == y:
        x+=1
    else:
        y+=1
    return x,y

def is_date(date_str,format1=None):
    formats = ["%d-%m-%Y","%d-%m-%y","%d/%m/%Y","%d/%m/%y"]
    if format1 != None:
        formats.extend(format1)
    for format in formats:
        try:
            datetime.strptime(date_str,format)
            return True
        except ValueError:
            pass
    return False

def read_line(txt,end): # still ambiguous :(  almost fixed :)
    if(end == len(txt)-1):
        return '',-1,-1
    while txt[end+1] == '\n':
        end+=1
    start = end+1
    end =  txt.find('\n',end+1)
    if end == -1:
        end = len(txt)-1
    return txt[start:end],start,end

# func to read only the first 'string' in the given index limit of a str. returns the 'valid' string and possible error (if next string falls within current string's range)
#[a func to read data in eaach cell]
def read_element(start_index, end_index, data_string,poss_next_element = None):
    iter = start_index
    valid_entry = ''
    read_text = 0 # 0-not reading, 1- read enabled, 2- read disabled;looking for errors
    while (iter < end_index):
        if(data_string[iter] != ' ') and ((data_string[iter-1] == ' ' and data_string[iter-2] == ' ') or (iter == 0 or iter-1 == 0) )and read_text == 0: #checkin if the word really starts in this range
            read_text = 1
            if poss_next_element == iter  :
                poss_next_element = None

        if((data_string[iter] != ' ' and data_string[iter] != '\n') or (data_string[iter] == ' ' and data_string[iter-1] != ' ' and (data_string[iter+1] !=  ' ' ))) and read_text == 1: #checkin if the word doesnt break
            valid_entry += data_string[iter]

        elif(read_text == 1 and iter == end_index-1): # if the word reaches end of range [cell end]
            if (iter != len(data_string)-1 and data_string[iter+1] != ' ' and data_string[iter+2] != ' ' ): # checkin if it really ends there
                valid_entry = ''

        elif(read_text == 1): #if the word fails to continue (breaks)
            read_text = 2
            
        if(read_text == 2 and data_string[iter] != ' ' and poss_next_element is None): #if second word in the range -records its index
            poss_next_element = iter
            read_text = 3
        iter+=1 #iter = iter+1 --hint for noobs
    return valid_entry,poss_next_element

def is_valid_amt(amt): 
    amt_copy = amt
    try:
        if amt_copy[-3] == '.' and float(amt_copy.replace(',','')):
            return True
    except:
        return False


def is_valid_transaction(benchmark,test):
    for x,y in zip(benchmark[-1],test):
        if 'M' in x :
            if y == '':
                # print(y,'failed in M')
                return False
    for x,y in zip(benchmark[-1],test):
        if 'D' in x :
            if not is_date(y):
                # print(y,'failed in D')
                return False
    count = 0
    for x,y in zip(benchmark[-1],test):
        if 'O' in x :
            if is_valid_amt(y):
                count+=1
    if count != 1:
        # print(count,'failed in O')
        return False
    return True 

# old convert_to_text() spot

def create_output_dirs(text_dir_path,output_dir_path):
    try:
        # print(text_dir_path,output_dir_path)
        text_dir_path = Path(text_dir_path)
        output_dir_path = Path(output_dir_path)
        text_dir_path.mkdir(parents = True,exist_ok = True)
        output_dir_path.mkdir(parents = True,exist_ok = True)
        return True
    except Exception as e:
        print("There's an error in creating output directories.\nError",e)
        return False

def get_n_check_pw(input_file_path,output_file_path,has_password = False):
    file_password = ''
    if has_password == True:
        file_password = getpass("Enter password :")
    try:
        result = subprocess.run(["pdftotext","-layout","-upw",file_password,input_file_path,output_file_path],stdout = subprocess.PIPE, stderr = subprocess.PIPE, check = True)
        return True
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode()
        if "Incorrect password" in error_message:
            return False
        else:
            print("Error while opening input file::",e.stdout.decode())
            return None

def convert_to_txt(input_file_path,output_file_path):
    pw_passed = get_n_check_pw(input_file_path,output_file_path)
    if pw_passed == True:
        return True
    elif pw_passed == False:
        print("This file is password protected.\n")
        password_retry_counter = 0
        while(password_retry_counter < 3):
            if get_n_check_pw(input_file_path,output_file_path,has_password=True) == False:
                if password_retry_counter < 2:
                    print(f"Incorrect password, Retry [{2-password_retry_counter} attempt(s) left]\n")
                password_retry_counter += 1
            else:
                return True
    else:
        return False

def is_valid_path(path_to_check):
    input_path = Path(path_to_check)
    if input_path.exists():
        return True
    return False

def supports_ansi():
    # Check if output is a terminal (not a pipe or file)
    if not sys.stdout.isatty():
        return False
    
    # Check for ANSI-supporting terminal
    term = os.getenv("TERM", "")
    if term in ("dumb", ""):
        return False

    # Windows-specific check
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            mode = ctypes.c_uint()
            if kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(mode)):
                return True
        except Exception:
            return False
        return False

    return True  # Assume ANSI support for Unix-like systems