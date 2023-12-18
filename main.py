#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import glob
import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

def parse_transcriptions(files):
    xml_files = glob.glob(files + "/**.xml", recursive=True)
    print("Found %d files" % len(xml_files))
    print(xml_files)
    root = ET.Element('root')
    xml_element_tree = ET.ElementTree(root)
    for xml_file in xml_files:
        data = ET.parse(xml_file).getroot()

        # At least for Hugo de Groot,
        # transcribed letters are <div> elements with the subtype 'artifact'
        # whereas subtype 'replaced-artifact' seem to be unavailable (some other collection)? Or duplicates?
        # TODO add useful replaced-artifact divs?
        for result in data.iterfind("./text/body/div[@subtype='artifact']"):
            root.append(result)
    print(ET.tostring(root.find("./")))
    return root

# For now, just use the available metadata and not the transcription

# Dates are listed as year, year-month, year-month-date or year-month/year-month or ?
# Just pick the first year available
def plot_timeline(root_elem):
    metadata = []
    datelist = []
    # Will only be used for matching from the beginning anyway
    year_pattern = re.compile('\d{4}')
    for letter in root_elem.iterfind("./div/interpGrp"):
        date = letter.find("./interp[@type='date']")
        year = year_pattern.match(date.get('value'))
        if year is not None:
            datelist.append(int(year.group()))
            metadata.append({'lang': letter.find("./interp[@type='language']").get('value'), 'year': int(year.group())})
    print(len(datelist))
    datelist.sort()
    min_date = datelist[0]
    max_date = datelist[-1]
    x = np.arange(min_date, max_date+1) # arange is [start, stop)
    latin = np.zeros(len(x))
    french = np.zeros(len(x))
    dutch = np.zeros(len(x))
    # Very inefficient way of doing this but no point prematurely optimizing
    for i in range(0, len(x)):
        year = x[i]
        for letter in metadata:
            if letter['year'] == year:
                if letter['lang'] == 'la':
                    latin[i] += 1
                elif letter['lang'] == 'fr':
                    french[i] += 1
                elif letter['lang'] == 'nl':
                    dutch[i] += 1

    plt.figure(figsize=(5, 2.7), layout='constrained')
    plt.plot(x, latin, label='Latin')
    plt.plot(x, french, label='French')
    plt.plot(x, dutch, label='Dutch')
    plt.xlabel('Year')
    plt.ylabel('Number of letters')
    plt.title("Language used in letters over time")
    plt.legend()
    plt.show()

# Currently only looking at de Groot, expand to the rest later
letters = parse_transcriptions('ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/groo001/')
plot_timeline(letters)
