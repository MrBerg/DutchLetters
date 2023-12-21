#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import glob
import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import mpltern

def parse_transcriptions(files):
    xml_files = list()
    for file in files:
        xml_files.extend(glob.glob(file + "/**.xml", recursive=True))
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
    return root

# For now, just use the available metadata and not the transcription
# Dates are listed as year, year-month, year-month-date or year-month/year-month or ?
# Just pick the first year available for multi-year datings
# TODO what to do about other languages present (German at least)?
def parse_metadata(root_elem):
    metadata = []
    # datelist could also probably be a set.
    datelist = []
    author_set = set()
    lang_set = set()
    # Will only be used for matching from the beginning anyway
    year_pattern = re.compile('\d{4}')

    for letter in root_elem.iterfind("./div/interpGrp"):
        author_node = letter.find("./interp[@type='sender']")
        author = author_node.get('value')
        date = letter.find("./interp[@type='date']")
        year = year_pattern.match(date.get('value'))
        # Some letters, especially in Leeuwenhoeck's corpus seem to lack the language element completely or specify it per <div> for summaries, paragraphs etc. Skip for now
        if letter.find("./interp[@type='language']") is None:
            print("%s %s" % (author, date.get('value')))
            continue
        language = letter.find("./interp[@type='language']").get('value')
        if year is not None and author != '?' and language != '?':
            datelist.append(int(year.group()))
            author_set.add(author)
            lang_set.add(language)
            metadata.append({'lang': language, 'author': author, 'year': int(year.group())})
    datelist.sort()
    min_date = datelist[0]
    max_date = datelist[-1]
    # Go from set to sorted list to make sure we keep the order for the following operations
    authors_list = list(author_set)
    authors_list.sort()
    print("Processed %d letters from %d–%d from %d senders in %d languages, having a specified date(range), sender and language" % (len(metadata), min_date, max_date, len(authors_list), len(lang_set)))
    print("Languages used: " + str(lang_set))
    return metadata, min_date, max_date, authors_list, lang_set


def plot_timeline(metadata, min_date, max_date):
    x = np.arange(min_date, max_date+1) # arange is [start, stop)
    latin = np.zeros(len(x))
    french = np.zeros(len(x))
    dutch = np.zeros(len(x))
    german = np.zeros(len(x))
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
                elif letter['lang'] == 'de':
                    german[i] += 1

    plt.figure()
    plt.plot(x, latin, label='Latin')
    plt.plot(x, french, label='French')
    plt.plot(x, dutch, label='Dutch')
    plt.plot(x, german, label='German')
    plt.xlabel('Year')
    plt.ylabel('Number of letters')
    plt.title("Language used in letters over time")
    plt.legend()
    timeline_file_name = 'timeline.png'
    plt.savefig(timeline_file_name)
    print("Figure saved to file %s" % timeline_file_name)
    #plt.show()
    #TODO figure out how to save these plots

# Here we want to find the proportions of letters in each language per sender (NB: not necessarily the author)
def plot_authors(root_elem, authors_list):
    authors = np.array(authors_list)
    totals = np.zeros(len(authors))
    latin = np.zeros(len(authors))
    french = np.zeros(len(authors))
    dutch = np.zeros(len(authors))
    german = np.zeros(len(authors))
    english  = np.zeros(len(authors))
    italian = np.zeros(len(authors))
    spanish = np.zeros(len(authors))
    greek = np.zeros(len(authors))
    portuguese = np.zeros(len(authors))
    for i in range(0, len(authors)):
        author = authors[i]
        for letter in metadata:
            if letter['author'] == author:
                # Hopefully we have already filtered out bad data
                totals[i] += 1
                if letter['lang'] == 'la':
                    latin[i] += 1
                elif letter['lang'] == 'fr':
                    french[i] += 1
                elif letter['lang'] == 'nl':
                    dutch[i] += 1
                elif letter['lang'] == 'de':
                    german[i] += 1
                elif letter['lang'] == 'en':
                    english[i] += 1
                elif letter['lang'] == 'it':
                    italian[i] += 1
                elif letter['lang'] == 'es' or letter['lang'] == 'spanish':
                    spanish[i] += 1
                elif letter['lang'] == 'grc':
                    greek[i] += 1
                elif letter['lang'] == 'pt':
                    portuguese[i] += 1

    # Look into the minor languages first TODO: discard before later stage?
    minor_lang_toplist = list(zip(authors, german, english, italian, spanish, portuguese, greek, totals))
    languages = ('German', 'English', 'Italian', 'Spanish', 'Portuguese', 'Ancient Greek')
    for i, lang in enumerate(languages):
        # Sort in reverse numerical order, only show those who have letters
        sorted_by_lang = sorted(minor_lang_toplist, key=lambda auth: auth[i+1], reverse=True)
        sorted_and_filtered = list(filter(lambda authr: authr[i+1] > 0, sorted_by_lang))
        print()
        print("Authors for %s" % lang)
        print("%-40s\t %s\t Total letters" % ("Name", lang))
        for author in sorted_and_filtered:
            print("%-40s:\t %d\t %d" % (author[0], author[i+1], author[-1]))

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
    #print()
    #print("Major languages only now")
    #print("%-40s\t Latin\t\t French\t\t Dutch\t\t Total" % "Name")
    #for i, author in enumerate(authors):
    #    print("%-40s:\t %f\t %f\t %f\t %d" % (author, latin_proportion[i], french_proportion[i], dutch_proportion[i], total_letters[i]))

    # Find most prolific authors to make less crowded graphs
    toplist = sorted(zip(authors, latin_proportion, french_proportion, dutch_proportion, total_letters), key=lambda author: author[4], reverse=True)
    filtered_toplist = list(filter(lambda auth: auth[-1] > 0, toplist))
    print()
    print("Top 100 authors")
    print("%-40s\t Latin\t\t French\t\t Dutch\t\t Total" % "Name")
    for i in range(0,100):
        print("%-40s:\t %f\t %f\t %f\t %d" % (toplist[i][0], toplist[i][1], toplist[i][2], toplist[i][3], toplist[i][4]))


    # For now, look only at senders using more than one language so as to not overwhelm in the plot
    # TODO: Also limit to senders with more than x letters
    filtered_only_major_langs = list(filter(lambda auth: auth[1]!= 1.0 and auth[2] != 1.0 and auth[3] != 1.0, filtered_toplist))
    # Unzip again to make plotting easier
    multilingual_authors, multiling_latin_prop, multiling_french_prop, multiling_dutch_prop, multiling_totals = zip(*filtered_only_major_langs)

    print("Found %d multilingual authors (major languages only)" % len(multilingual_authors))
    # Now the plotting begins
    # TODO: instead of doing a 3d plot, do a ternary scatterplot
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    xs = multiling_latin_prop
    ys = multiling_french_prop
    zs = multiling_dutch_prop
    ax.scatter(xs, ys, zs)
    for i, author in enumerate(multilingual_authors):
        ax.text(xs[i], ys[i], zs[i], author)

    ax.set_xlabel('Proportion of Latin')
    ax.set_ylabel('Proportion of French')
    ax.set_zlabel('Proportion of Dutch')
    plt.title('3d scatterplot of the proportions of Latin, French and Dutch letters')

    # Rotate the plot to a better perspective for viewing the gamut
    # Default is elev=30, azim=-60, roll=0
    ax.view_init(elev=60, azim=45, roll=0)
    scatter_3d_file_name = '3d_scatter.png'
    plt.savefig(scatter_3d_file_name)
    print("Figure saved to file %s" % scatter_3d_file_name)
    #plt.show()

    # Do a ternary plot
    # TODO fix the title positioning to appear inside figure
    fig_tern = plt.figure(layout="tight")
    ax_tern = fig_tern.add_subplot(projection="ternary")
    plt.title("Ternary plot of the proportions of letters in Latin, French and Dutch per sender")
    #plt.autoscale()
    ax_tern.set_tlabel("Latin")
    ax_tern.set_llabel("French")
    ax_tern.set_rlabel("Dutch")

    ax_tern.grid()
    ax_tern.scatter(xs, ys, zs)
    for i, author in enumerate(multilingual_authors):
        ax_tern.text(xs[i], ys[i], zs[i], author)
    ternary_file_name = 'ternary_plot.png'
    plt.savefig(ternary_file_name)
    print("Figure saved to file %s" % ternary_file_name)
    plt.show()

# Currently only looking at de Groot, Christiaan and Constantijn Huyghens, expand to the rest later when I have looked into their xml file layout
# Leeuwenhoek is also being skipped for now because of a different way of marking language
# Constantin Huyghens corpus also has the language listed for roughly 100 letters
folders = ['ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/groo001/', 'ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/huyg001/', 'ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/huyg003/']
letters = parse_transcriptions(folders)
metadata, min_date, max_date, authors_list, lang_set = parse_metadata(letters)
plot_timeline(metadata, min_date, max_date)
plot_authors(metadata, authors_list)
