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


header_params = [["date ","dt "],
                 ["particular","description","narration"],
                 ["withdrawal","debit","dr"],#maybe add receipt?
                 ["deposit","credit","cr"],#maybe add payments?
                 ["balance","bal"]]


def is_pdf(path):
    try:
        mime = filetype.guess(path).mime 
        if  mime == 'application/pdf':
            return True
    except Exception  as e:
        print('\tError:',e)
    return False

def file_path_compat(path):
    res = ''
    res_temp = ''
    last_index = len(path)-1
    for i in range(len(path)):
        res_temp+= path[i]
        if path[i] == os.sep or i == last_index :
            if res_temp.find(' ') == -1:
                res+= res_temp
            else:
                res+= f'"{res_temp[:-1]}"{os.sep}'
            res_temp = ''
    return res

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

def get_text_in_given_range(start,end,line): # retruns first text in the given range of str ;can be improvised -make start,end optional
    return line[start:end].strip().split('  ')[0]

def time_now(): 
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def read_pdf(input_file_path,debug_text_file=False): #read pdf and returns text as a list of, list of strings , -[pages[lines]] , so it has  -well remenber and use brain
    # second arg is text_file_path, if given, creates a text file (poppler output), else no
    from pathlib import Path # this wont be needed
    page_count = 0

    # optionally creating text-file
    if debug_text_file :
        path_debug_text_file = Path(debug_text_file)
        path_debug_text_file.parent.mkdir(parents=True,exist_ok=True)
        debug_file_name_t = f"{path_debug_text_file.with_suffix('')}{time_now()}{path_debug_text_file.suffix}"
        Path(debug_file_name_t).touch(exist_ok = False) 

    cmd = ["pdfinfo",input_file_path]
    page_info = subprocess.run(cmd,capture_output=True,text=True)
    for line in page_info.stdout.splitlines():
        if line.startswith("Pages"):
            page_count = line.split()[1]
    
    pdf_content = []
    for i in range(1,int(page_count)+1): # ;page starts at 1 and -l isnt included(exclusive)
        
        cmd = ["pdftotext", "-layout", "-f", str(i), "-l", str(i), input_file_path, "-"]
        page_content = subprocess.run(cmd,capture_output=True,check = True,text = True)
        if page_content.returncode == 0:
            pdf_content.append(page_content.stdout.splitlines())
            if debug_text_file :
                with open(debug_file_name_t,"a") as debug_text:
                    for line in page_content.stdout.splitlines():
                        debug_text.write(f"{line}\n")
                    
        else:
            print("..Error:",page_content.stderr,f"\n while processing page no. #{i}")
            return False
    return pdf_content

def is_header(line,line_index,header_params,text=None):  # well,text= its the text of the page  ;header_params= possible values for core cols (eg date, particular, etc)
    judge = set()  
    if "date" in line.lower(): 
        for header in header_params:
            judge = set()
            for head in header:
                if text:
                    stacked_headers = [line+text[line_index-1],line+text[line_index+1],text[line_index-1]+line+text[line_index+1]]
                    for stacked_header_index,stacked_header in enumerate(stacked_headers):
                        if head.lower() in stacked_header.lower():
                            judge.add(stacked_header_index+2)
                            continue
                else:
                    if head.lower() in line.lower():
                        judge.add(True)
                        continue
       
    if True in judge:
        return True
    elif 2 in judge:
        return 2
    elif 3 in judge:
        return 3
    elif 4 in judge:
        return 4
    return False

def get_headers(text,header_line_indices): # basically prepares atr[0,1,2] -3,4 ar33 made from dividers[]
    header_datas = [[],[],[]]
    # header_lines_count = len(header_line_indices)
    len_longest_header = 0
    for i in header_line_indices:
        if len_longest_header < len(text[i]):
            len_longest_header = len(text[i])
            # print('$$$$$$$$$$$$$$$$$$$$$$$$$$',text[i])
    print('l_head:',len_longest_header)
    in_soviet_sector = False
    for i in range(len_longest_header+1):
        fk = set()
        for j in header_line_indices:
            if not in_soviet_sector and i<len(text[j]) and text[j][i] != " ": 
                # print('startpoint:',i)
                header_datas[1].append(i) # setting start-point of col header
                in_soviet_sector = True
                break
            elif in_soviet_sector:
                
                if ( i>=len(text[j])-1 or (i<len(text[j])-1 and (text[j][i+1] == ' ' and text[j][i+2] == ' '))): #setting end-point of col header
                    fk.add(True)
                else:
                    fk.add(False)   

        if in_soviet_sector and True in fk and False not in fk:
            # print('endpoint:',i,fk)
            header_datas[2].append(i) # setting end-point of col header
            header_datas[0].append(get_contents_of_2d_list(text[min(header_line_indices):max(header_line_indices)+1],header_datas[1][-1],header_datas[2][-1])) # setting col header content
            in_soviet_sector = False
    # header_datas[1] = [x+1 for x in range(len(header_datas[2]))
    def get_american_sectors(x,y):
        # print('debug:',x,y)
        for i in range(len(x)):
            # print('##:',i)
            x[i] = y[i]+1
            if i < len(x)-1:
                y[i] = x[i+1]
            else:
                y.pop(-1)
        # return x,y
    # print('dat',header_datas)
    get_american_sectors(header_datas[1],header_datas[2])
    return header_datas #atr

# def make_atrs(text,american_sectors): # text is all text in a page of pdf , american_sectors is list of range of empty cols between headers
#     for sector in american_sectors:
#         for col in text[sector[0]]:


def get_contents_of_2d_list(list,start_col,end_col): # maybe add optional row constrains and use this to extract data fields?
    # can combine words in consecutive rows by cols -explain engine dead, try in runtime :(
    # btw, im dead already [01-05-2025]
    res = ''
    for i in range(len(list)):
        res+=' '+list[i][start_col:end_col+1].strip()
    return res.strip()


