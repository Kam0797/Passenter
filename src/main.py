# Distributed under GNU GPL version-3  licence.
# Passbook_to_excel.[Passenter] version : 0.3

# Copyright (C) 2025, Kam <gv.kamal2003@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


#################################
# from datetime import datetime
# import os
# import subprocess
# import sys
# from pathlib import Path
# from getpass import getpass

from settings import * #dont delete it!


# root_path imported from src/settings
venv_path = os.path.join(root_path,"p_env")

if os.name == "nt":
    import setup_windows
else:
    import setup_linux
# import py_setup # imported in passenter.py

from functions import *

# import filetype
# from openpyxl import Workbook




 
if supports_ansi():
    print(f"\n\t\033[1;36mPassenter :\033[0m \033[36mA cool tool to covert passbooks to .xlsx \033[0m\n\t\033[34mSource code at\033[0m \033[4;34mhttps://github.com/Kam0797/Passenter\033[0m\n\t\033[33mdo drop your comments at \033[4mgv.kamal2003@gmail.com\033[0m\n ")
else:
    print(f"\n\tPassenter : A cool tool to covert passbooks to .xlsx \n\tSource code at https://github.com/Kam0797/Passenter\n\tdo drop your comments at gv.kamal2003@gmail.com\n ")

# print(colored('Passenter : A cool tool to covert passbooks to .xlsx','cyan',attrs=[]))
while True:
    INPUT_FILE_PATH = input("Enter file path [you can drag 'n drop!][or 'e' to exit]: ").replace("'",'').strip()
    if INPUT_FILE_PATH == 'e' or INPUT_FILE_PATH == 'E':
        print("Bye!")
        exit()
    elif INPUT_FILE_PATH == '':
        print("\tInput file path is empty, Enter a valid path")
    
    elif not is_valid_path(INPUT_FILE_PATH):
        print("\tSuch a file doesn't exist.")

    # INPUT_FILE_PATH = INPUT_FILE_PATH.replace("'",'').strip() //rm this too
    # INPUT_FILE_PATH = INPUT_FILE_PATH.strip()  //rm this
    #req: folders with ' ' cause errors. paths with them be modified to have ~/"folder name"/*
    # print(f"#{INPUT_FILE_PATH}#")
    # print(is_pdf(INPUT_FILE_PATH))
    # print("****")
    elif is_pdf(INPUT_FILE_PATH):
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



        merge_choice = input("Does the header row have stacked words? (y/N):")
        if get_merge_choice(merge_choice):
            merge = True
                
    #   print(TEXT_DIR_PATH,OUTPUT_DIR_PATH)
        create_output_dirs(TEXT_DIR_PATH,OUTPUT_DIR_PATH)

        print("Input file: ",INPUT_FILE_PATH[file_name_start_index:]) #@@
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
            if supports_ansi:
                print("\033[1;32mprobably done!\033[0m")
            else:
                print("probably done!")
    else:
        print("\tThe input file doesn't seem to be a pdf file...[or some other error] check it" )
    print('\nthen,')
print("Bye!")            

            
 

            
