# Passenter

A cross-platform tool to convert passbooks(in .pdf) to spreadsheets

Hey . 

#### Software Requirement:

Python -version >3.11

#### How to:

* clone the repo / get the .zip and extract or ...

* `git clone https://github.com/Kam0797/Passenter.git` [you'll need git]

* `cd Passenter`

* `python passenter.py`

  

* For windows, add:
  
  `p_env\Scripts\activate && python passenter.py`
  
  things should go well

#### output:

* two dirs are created at the path of input file, at runtime (if they dont exist already)
* text_passenter --has passbook text
* outputs_passenter --has output (spreadsheet) in .xlsx format 
  This is a [intended to be] cool tool to convert passbooks in .pdf formats into spreadsheets
  This can be helpful while feeding fin. data to accounting software.

yeah.. bugs exist..

#### known bugs:

* last entry doesnt appear in spreadsheet (you'd have to enter it manually)

* first column of input data should contain 'date's 

* inaccuracies with 'stacked headers'

* For windows, 
  
  additional step [only on first time]:
  
   ```p_env\Scripts\activate && python passenter.py```

#### ToDo:

- MacOS support

- ... 

Have thoughts to share about this work?
    feel free to send an email at  gv.kamal2003@gmail.com
