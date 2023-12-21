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

    plt.figure()
    plt.plot(x, latin, label='Latin')
    plt.plot(x, french, label='French')
    plt.plot(x, dutch, label='Dutch')
    plt.xlabel('Year')
    plt.ylabel('Number of letters')
    plt.title("Language used in letters over time")
    plt.legend()
    plt.show()
    #TODO figure out how to save these plots

# Do it again in a stupid way for now, later combine metadata generation and filtering
# Here we want to find the proportions of letters in each language per sender (NB: not necessarily the author)
# We should do it in the same step to get only letters with declared languages
def plot_authors(root_elem):
    metadata = []
    author_set = set()
    for letter in root_elem.iterfind("./div/interpGrp"):
        author_node = letter.find("./interp[@type='sender']")
        author = author_node.get('value')
        if author != '?':
            author_set.add(author)
            metadata.append({'lang': letter.find("./interp[@type='language']").get('value'), 'author': author})
    print(len(author_set))

    # Go from set to sorted list to make sure we keep the order for the following operations
    authors_list = list(author_set)
    authors_list.sort()
    authors = np.array(authors_list)
    latin = np.zeros(len(authors))
    french = np.zeros(len(authors))
    dutch = np.zeros(len(authors))
    for i in range(0, len(authors)):
        author = authors[i]
        for letter in metadata:
            if letter['author'] == author:
                if letter['lang'] == 'la':
                    latin[i] += 1
                elif letter['lang'] == 'fr':
                    french[i] += 1
                elif letter['lang'] == 'nl':
                    dutch[i] += 1

    # Could probably use actual numpy methods but haven't yet got the time to do so
    latin_proportion = np.zeros(len(authors))
    french_proportion = np.zeros(len(authors))
    dutch_proportion = np.zeros(len(authors))
    total_letters = np.zeros(len(authors))
    for i in range(0, len(authors)):
        total_letters[i] = latin[i] + french[i] + dutch[i]
        latin_proportion[i] = latin[i] / total_letters[i]
        french_proportion[i] = french[i] / total_letters[i]
        dutch_proportion[i] = dutch[i] / total_letters[i]

    # Print a nice table of the results TODO: actually a nice looking one using some library
    # Reserve 40 chars for the names
    #print("%-40s\t Latin\t\t French\t\t Dutch\t\t Total" % "Name")
    #for i, author in enumerate(authors):
    #    print("%-40s:\t %f\t %f\t %f\t %d" % (author, latin_proportion[i], french_proportion[i], dutch_proportion[i], total_letters[i]))

    # Find most prolific authors to make less crowded graphs
    toplist = sorted(zip(authors, latin_proportion, french_proportion, dutch_proportion, total_letters), key=lambda author: author[4], reverse=True)
    print("Top 100 authors")
    print("%-40s\t Latin\t\t French\t\t Dutch\t\t Total" % "Name")
    for i in range(0,100):
        print("%-40s:\t %f\t %f\t %f\t %d" % (toplist[i][0], toplist[i][1], toplist[i][2], toplist[i][3], toplist[i][4]))


    # For now, look only at senders using more than one language so as to not overwhelm in the plot
    # Let anyone with nan values slip through for now, they won't be plotted anyway
    # TODO: make lists of the monolingual authors and the amount of letters they have written
    multilingual_authors = list()
    multiling_latin_prop = list()
    multiling_french_prop = list()
    multiling_dutch_prop = list()
    for i, author in enumerate(authors):
        if latin_proportion[i] != 1.0 and french_proportion[i] != 1.0 and dutch_proportion[i] != 1.0:
            multilingual_authors.append(author)
            multiling_latin_prop.append(latin_proportion[i])
            multiling_french_prop.append(french_proportion[i])
            multiling_dutch_prop.append(dutch_proportion[i])

    print("Found %d multilingual authors" % len(multilingual_authors))
    # Now the plotting begins
    # TODO: instead of doing a 3d plot, do a ternary scatterplot
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    #xs = latin_proportion
    #ys = french_proportion
    #zs = dutch_proportion
    #ax.scatter(xs, ys, zs)
    #for i, author in enumerate(authors):
    #    ax.text(xs[i], ys[i], zs[i], author)

    xs = multiling_latin_prop
    ys = multiling_french_prop
    zs = multiling_dutch_prop
    ax.scatter(xs, ys, zs)
    for i, author in enumerate(multilingual_authors):
        ax.text(xs[i], ys[i], zs[i], author)

    ax.set_xlabel('Proportion of Latin')
    ax.set_ylabel('Proportion of French')
    ax.set_zlabel('Proportion of Dutch')

    # Rotate the plot to a better perspective for viewing the gamut
    # Default is elev=30, azim=-60, roll=0
    ax.view_init(elev=60, azim=45, roll=0)
    plt.show()

# Currently only looking at de Groot, expand to the rest later
letters = parse_transcriptions('ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/groo001/')
plot_timeline(letters)
plot_authors(letters)
