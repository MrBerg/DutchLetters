#Dutch letters: a final project for the Computational literacy course
##By Jonas Berg

#Requirements to replicate
Python 3 (TODO version? I'm on 3.9)
xml.etree.ElementTree (TODO stdlib?)
glob (stdlib?)
matplotlib 3.8.2
mpltern 1.0.2
numpy 1.26.2

Older versions of matplotlib, mpltern and numpy probably work as well.

The required libraries are hopefully easily just by running `pip install -r requirements.txt` from this folder
or maybe `python3 -m pip install -r requirements.txt` to ensure you are actually using python3

To get access to the data, download the CKCC data from [their gitlab] or [archived data] and extract it into this folder.
TODO: check if I can redistribute.

To run the program, just run `python3 main.py` from this folder, most of the output will be to stdout
and the figures will be in popup windows. You need to close the window to have the program move forward.
