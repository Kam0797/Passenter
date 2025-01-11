# Distributed under GNU GPL version-3  licence.
# Passbook_to_excel.[Passenter] version : 0.3
# This maybe considered the first alpha version of this application


#################################
from datetime import datetime
import os
import subprocess
import sys
from pathlib import Path
from getpass import getpass


from settings import * #dont delete it!

root_file = os.path.abspath(__file__)
root_path = os.path.dirname(root_file)
venv_path = os.path.join(root_path,"p_env")
# print('k',root_path)

if os.name == "nt":
    import setup_windows
else:
    import setup_linux
import py_setup
# breakpoint()
import filetype
from openpyxl import Workbook


def is_pdf(path):
    try:
        mime = filetype.guess(path).mime == 'application/pdf'
        return True
    except Exception  as e:
        print('Error:',e)
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

# def convert_to_txt(path):
#     from getpass import getpass
#     try:
#         subprocess.run(["pdftotext", "-layout", f"{INPUT_FILE_PATH}", f"{TEXT_DIR_PATH}{TEXT_FILE}"])
#         return path
#     except Exception as e:
#         print('Error:',e)
#     return False

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
    print(pw_passed)
    if pw_passed == True:
        return True
    elif pw_passed == False:
        print("This file is password protected.\n")
        password_retry_counter = 0
        # while(get_n_check_pw("kris0593.pdf","kris.txt",has_password=True) == False and password_retry_limit < 2):
        while(password_retry_counter < 3):
            if get_n_check_pw(input_file_path,output_file_path,has_password=True) == False:
                print(f"Incorrect password, Retry [{2-password_retry_counter} attempts left]\n")
                password_retry_counter += 1
            # elif password_retry_counter <2:
            else:
                return True
    else:
        return False

INPUT_FILE_PATH = input("Enter file path [or you can drag 'n drop!]: ")
INPUT_FILE_PATH = INPUT_FILE_PATH.replace("'",'')
INPUT_FILE_PATH = INPUT_FILE_PATH.strip()
#req: folders with ' ' cause errors. paths with them be modified to have ~/"folder name"/*
# print(f"#{INPUT_FILE_PATH}#")
# print(is_pdf(INPUT_FILE_PATH))
# print("****")

if is_pdf(INPUT_FILE_PATH):
    print("ispdf",is_pdf(INPUT_FILE_PATH),INPUT_FILE_PATH)
    file_name_start_index,file_name_end_index = -1,-1
    i = len(INPUT_FILE_PATH)-1
    while i>0:
        if INPUT_FILE_PATH[i] == '.' and file_name_end_index == -1:
            file_name_end_index = i
        if (INPUT_FILE_PATH[i] == '/' or INPUT_FILE_PATH[i] == '\\') and file_name_start_index == -1:
            file_name_start_index = i+1
        i-=1
    if(file_name_start_index == -1):
        file_name_start_index = 0
    
    # print('jk',file_name_start_index,file_name_end_index)
    if file_name_start_index != -1 and file_name_end_index != -1:
        FILE_NAME = INPUT_FILE_PATH[file_name_start_index:file_name_end_index]
        INPUT_DIR_PATH = INPUT_FILE_PATH[:file_name_start_index]

        TEXT_DIR,SPREADSHEET_OUTPUT_DIR = "text_passenter","outputs_passenter"
        TEXT_DIR_PATH = f"{INPUT_DIR_PATH}{TEXT_DIR}{os.sep}"
        OUTPUT_DIR_PATH = f"{INPUT_DIR_PATH}{SPREADSHEET_OUTPUT_DIR}{os.sep}"


        TEXT_FILE = FILE_NAME + '.txt'
        OUTPUT_FILE = FILE_NAME + '.xlsx' #ambiguous /8.1.2 -no more


    else:
        print("\nThe input file doesn't seem to be a pdf file...[or some other error] check it" )



    merge_choice = input("Does the header row have stacked words? (y/N):")
    if get_merge_choice(merge_choice):
        merge = True
            
 #   print(TEXT_DIR_PATH,OUTPUT_DIR_PATH)
    create_output_dirs(TEXT_DIR_PATH,OUTPUT_DIR_PATH)

    print("Input file: ",TEXT_FILE,'\nder :') #@@
    print(INPUT_FILE_PATH,f"{TEXT_DIR_PATH}{TEXT_FILE}")
    if(convert_to_txt(INPUT_FILE_PATH,f"{TEXT_DIR_PATH}{TEXT_FILE}")):
        with open(f"{TEXT_DIR_PATH}{TEXT_FILE}",'r') as file: 

            txt = file.read()

        #~~ regret this --to be fixed,rewritten,scrapped
            dp1,dp2,d3 = -1,-1,-1
            dp1 = txt.find('  Date  ')
            dp2 = txt.find('  DATE  ')
            dp3 = txt.find('DATE  ')

            if dp3 != -1:
                dp = dp3
            elif dp2 != -1:
                dp = dp2
            elif dp1 != -1:
                dp = dp1
            else:
                print('#err "dp still empty"')


            i = dp
            count = 0
            while(count<2):
                if txt[i] == '\n' and count == 0:
                    l2 = i+1
                    count+=1
                elif txt[i] == '\n' and count ==1:
                    count+=1 
                i-=1 
            l1 = i+2

            i = dp

        #~~ regrets 

            count = 0
            while(count<1):
                if txt[i] == '\n' :
                    l3 = i+1
                    count+=1
                i+=1

            atr1=[[],[],[]]
            atr2=[[],[],[]] 
            atr3=[[],[],[]]


        # Making atr1
            i = l1
            temp_word = ''
            word_start = False
            while txt[i] != '\n':
                extract_range(txt,l1,i,None,atr1)
                i+=1

        # Making atr3
            i = l3
            temp_word = ''
            word_start = False
            while txt[i] != '\n':
                extract_range(txt,l3,i,None,atr3)
                i+=1

        # Making atr2
            i = l2
            temp_word = ''
            word_start = False
            while txt[i] != '\n':
                extract_range(txt,l2,i,None,atr2)
                i+=1

            if atr1 != [[],[],[]] and atr3 != [[],[],[]] and atr2[2][-1] < max(atr1[2][-1],atr3[2][-1]): # the 'and': a literal temporary soln #1
                    #adjusting for last attribs in atr1,atr3
                atr2[1].append(max(atr1[2][-1],atr3[2][-1]))
                atr2[2].append(max(atr1[2][-1],atr3[2][-1]))
            else:
                
                atr2[1].append(atr2[2][-1]+1)
                atr2[2].append(atr2[2][-1]+1)
            atr2[0].append('None')



        ##>

        # Eto merge  
            l1_index,l3_index = 0,0
            x,y = 0,0
            atr = [[],[],[]]
            while (x != len(atr2[0]) and y != len(atr2[0])-1 and atr_merge == True) :
                # print(x,y)
                temp_word = ''
                temp_int_en ,temp_int_st = [],[]
                temp_int_main = None
                if(atr1 != [[],[],[]] and ((atr2[1][x] <= atr1[1][l1_index] and atr2[2][y] >= atr1[2][l1_index]) or (atr2[1][x] >= atr1[1][l1_index] and atr2[2][y] <= atr1[2][l1_index]))):
                    temp_word += atr1[0][l1_index]
                    temp_int_st.append(atr1[1][l1_index])
                    l1_index+=1
                if(x == y):
                    temp_word += atr2[0][x]
                    temp_int_main = [atr2[1][x],atr2[2][x]]
                if(atr3 != [[],[],[]] and ((atr2[1][x] <= atr3[1][l3_index] and atr2[2][y] >= atr3[2][l3_index]) or (atr2[1][x] >= atr3[1][l3_index] and atr2[2][y] <= atr3[2][l3_index]))):
                    temp_word += atr3[0][l3_index]
                    temp_int_en.append(atr3[2][l3_index])
                    l3_index+=1

                if temp_word != '':
                    atr[0].append(temp_word)
                    if temp_int_main != None:
                        atr[1].append(temp_int_main[0])
                        atr[2].append(temp_int_main[1])
                    else:
                        atr[1].append(min(temp_int_st))
                        atr[2].append(max(temp_int_en))
                x,y = incr_xy(x,y)
            ## there's a potential bug. the above code doesnt consider >1 consequent attribs in atr1 and atr2.
            ##> need to fix in futr (idea:incr l1_index when atr1[2][l1_index] < atr2[1][x] ) >>have to be func-ed

            if atr_merge is not True:
                atr = atr2
            atr[1][-1] = (atr[1][-1]+15) #adding end-limit for last atr

            # appending mean_list
            atr.append([0,*[round((atr[2][x]+atr[1][x+1])/2) for x in range(len(atr[2])-1)]])

            # adding --flags 
            atr.append([[] for _ in atr[0]]) # empty template, 
            for index,title in enumerate(atr[0]): 
                if ('date' in title.lower() or 'particulars' in title.lower() or 'narration' in title.lower() or 'balance' in title.lower()) and atr[4][index] == []:
                    atr[4][index].append('M') #mandatory
                if (('particulars' in title.lower() or 'narration' in title.lower()) and 'M' in atr[4][index]):
                    atr[4][index].append('P') #particulars (appending allowed)
                if ('withdrawal' in title.lower() or 'deposit' in title.lower()) and atr[4][index] == []:
                    atr[4][index].append('O') #optional (xor)
            atr[4][0].append('D') # date column
            

            for index,i in enumerate(atr[4]):
                if 'P' in i:
                    atr[3][index] = atr[2][index-1] +1
            # print(atr[2],atr[3])

            # print(atr) ##### debug useful [8.1]


        y = 0 
        transactions = []
        errors = []
        misc = []
        line = ''
        pos = None
        fk=0
        temp_transaction = ['' for _ in atr[2]]

        while (x != -1 and y != -1  ):
            line,x,y = read_line(txt,y)
            pos = None
            temp_pos = None
            i = 0
            while( i < len(atr[3])-1 and atr[3][i] < len(line)):
                element,pos = read_element(atr[3][i],min(atr[1][i+1],len(line)),line,pos)     
                    
                if ('D' in atr[4][i] and is_date(element) == True) or (pos == temp_pos and pos != None):

                    # if (pos == temp_pos and pos != None):

                    if(is_valid_transaction(atr,temp_transaction)):
                        temp_transaction[-1] = len(transactions)+len(errors)+len(misc)
                        transactions.append(temp_transaction)

                    elif is_date(temp_transaction[0]):
                        errors.append(temp_transaction)
                    else:
                        misc.append(temp_transaction)
                    temp_transaction = ['' for _ in atr[2]]

                if 'P' in atr[4][i] :
                    temp_transaction[i] += element
                elif temp_transaction[i] == '':
                    temp_transaction[i] = element
                temp_pos = pos

                i+=1
        workbook = Workbook()
        sheet = workbook.active

        for row in transactions:
            sheet.append(row)

        workbook.save(f"{os.path.join(OUTPUT_DIR_PATH,OUTPUT_FILE)}")

        # for row in transactions:
        #     print(row)
        # print(errors)
        # print(misc)
        print("probably done!")
        

        
