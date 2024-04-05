#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import glob
import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import mpltern

# This method reads the suitable files in the folders and collects the metadata for
# the letters, returning an XML structure
def parse_transcriptions(folders):
    # Create a new xml tree for matching XML elements
    root = ET.Element('root')
    for folder in folders:
        # Some corpuses have proper xml files, some have concatenated xml files into txt files
        xml_files = list(glob.glob(folder + "/**.xml", recursive=True))
        txt_files = list(glob.glob(folder + "/**.txt", recursive=True))
        print("Found %d XML files and %d TXT files" % (len(xml_files), len(txt_files)))
        xml_element_tree = ET.ElementTree(root)
        for xml_file in xml_files:
            data = ET.parse(xml_file).getroot()
            # At least for Hugo de Groot,
            # transcribed letters are <div> elements with the subtype 'artifact'
            # whereas subtype 'replaced-artifact' seem to be unavailable (some other collection)? Or duplicates?
            # TODO add useful replaced-artifact divs?
            for result in data.iterfind("./text/body/div[@subtype='artifact']"):
                root.append(result)
        # txt files use lines like '### 0001.xml' and '### EOF' to separate the <TEI> roots for each letter
        # also they are not always proper xml, so we drop the letter contents without even parsing them
        # by just saving the renamed <teiHeader> subtrees under a new <div> elem to follow the xml structure above.
        # It should be fine to have all the letters in a file share the same root.
        for txt_file in txt_files:
            txt_file = open(txt_file, 'r').readlines()
            edited_file = []
            for line in txt_file:
                if line.startswith("<teiHeader") or line.startswith("</teiHeader>") or line.startswith("<meta"):
                    # Do a basic find-replace to make later parsing easier
                    line = re.sub('<teiHeader', '<interpGrp', line)
                    line = re.sub('</teiHeader', '</interpGrp', line)
                    line = re.sub('<meta', '<interp', line)
                    edited_file.append(line)
            if edited_file:
                recombined_string = "<div>\n" + "".join(edited_file) + "</div>"
                data = ET.fromstring(recombined_string)
                root.append(data)
    return root

# This method goes through the metadata and drops letters which lack an author, date or listed language
# Dates are listed in the metadata as year, year-month, year-month-date or year-month/year-month or ?
# Just pick the first year available for multi-year datings
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
        # If there is no sender node, it is probably not a letter
        if author_node is None:
            continue
        author = author_node.get('value')
        date = letter.find("./interp[@type='date']")
        year = year_pattern.match(date.get('value'))
        # Some letters, especially in Leeuwenhoeck's corpus seem to lack the language element completely or specify it per <div> for summaries, paragraphs etc. Skip those for now
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

def plot_timeline(ego, metadata, min_date, max_date, mode):
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

    # First plot absolute amount of letters in each major language
    plt.figure(figsize=(8,6))
    plt.plot(x, latin, label='Latin')
    plt.plot(x, french, label='French')
    plt.plot(x, dutch, label='Dutch')
    plt.plot(x, german, label='German')
    plt.xlabel('Year')
    plt.ylabel('Number of letters')
    plt.title("Language used in letters over time for %s %s" % (mode, ego))
    plt.legend()
    timeline_file_name = "timeline_%s.png" % re.sub(' ', '_', mode + "_" + ego)
    plt.savefig(timeline_file_name)
    print("Figure saved to file %s" % timeline_file_name)
    plt.show()

    # Then plot the relative amount of letters over time
    # first we calculate the proportions, could probably do it more efficiently with some numpy methods
    prop_latin = np.zeros(len(x))
    prop_french = np.zeros(len(x))
    prop_dutch = np.zeros(len(x))
    prop_german = np.zeros(len(x))
    for i in range(0, len(x)):
        sum = latin[i] + french[i] + dutch[i] + german[i]
        prop_latin[i] = latin[i]/sum
        prop_french[i] = french[i]/sum
        prop_dutch[i] = dutch[i]/sum
        prop_german[i] = german[i]/sum
    plt.figure(figsize=(8,6))
    plt.stackplot(x, prop_latin, prop_french, prop_dutch, prop_german, labels=('Latin', 'French', 'Dutch', 'German'))
    plt.xlabel('Year')
    plt.ylabel('Proportion of letters')
    plt.title("Proportion of language used in letters over time for %s %s" % (mode, ego))
    plt.legend(loc='lower left') # TODO figure out how to put legend outside of figure
    stack_file_name = "stack_%s.png" % re.sub(' ', '_', mode + "_" + ego)
    plt.savefig(stack_file_name)
    print("Figure saved to file %s" % stack_file_name)
    plt.show()

# Here we want to find the proportions of letters in each language per sender (NB: not necessarily the author)
# TODO split into sent/received?
def plot_authors(ego, root_elem, authors_list):
    print("Language proportion for %s's correspondence" % ego)
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

    # Find most prolific authors to make less crowded graphs
    toplist = sorted(zip(authors, latin_proportion, french_proportion, dutch_proportion, total_letters), key=lambda author: author[4], reverse=True)
    filtered_toplist = list(filter(lambda auth: auth[-1] > 0, toplist))
    print()
    print("Top 100 authors for %s" % ego)
    # Reserve 40 chars for the names
    print("%-40s\t Latin\t\t French\t\t Dutch\t\t Total letters (in these languages)" % "Name")
    # Need to clamp max value for ego networks with <100 correspondents
    for i in range(0,min(100, len(toplist))):
        print("%-40s:\t %f\t %f\t %f\t %d" % (toplist[i][0], toplist[i][1], toplist[i][2], toplist[i][3], toplist[i][4]))

    # For now, look only at senders using more than one language so as to not overwhelm in the plot
    # TODO: Also limit to senders with more than x letters
    filtered_only_major_langs = list(filter(lambda auth: auth[1]!= 1.0 and auth[2] != 1.0 and auth[3] != 1.0, filtered_toplist))
    # Unzip again to make plotting easier
    multilingual_authors, multiling_latin_prop, multiling_french_prop, multiling_dutch_prop, multiling_totals = zip(*filtered_only_major_langs)
    print()
    print("Found %d multilingual authors (major languages only) for %s" % (len(multilingual_authors), ego))
    print("%-40s\t Latin\t\t French\t\t Dutch\t\t Total letters (in these languages)" % "Name")
    for i in range(0,len(multilingual_authors)):
        print("%-40s:\t %f\t %f\t %f\t %d" % (multilingual_authors[i], multiling_latin_prop[i], multiling_french_prop[i], multiling_dutch_prop[i], multiling_totals[i]))

    # Now the plotting begins
    # This 3d plot and the ternary scatterplot show the same data but one might be more readable
    # TODO: add the monolingual authors, make either one a heatmap?
    fig = plt.figure(figsize=(10,8))
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
    plt.title('3d scatterplot of the proportions of Latin, French and Dutch letters for %s' % ego)

    # Rotate the plot to a better perspective for viewing the plane they are all in
    # Default is elev=30, azim=-60, roll=0
    ax.view_init(elev=60, azim=45, roll=0)
    scatter_3d_file_name = "3d_scatter_%s.png" % re.sub(' ', '_', ego)
    plt.savefig(scatter_3d_file_name)
    print("Figure saved to file %s" % scatter_3d_file_name)
    plt.show()

    # Do a ternary plot
    fig_tern = plt.figure(figsize=(10,8), layout='constrained')
    ax_tern = fig_tern.add_subplot(projection="ternary")
    ax_tern.set_title("Proportions of letters in Latin, French and Dutch per sender for %s" % ego)
    ax_tern.set_tlabel("Latin")
    ax_tern.set_llabel("French")
    ax_tern.set_rlabel("Dutch")

    ax_tern.grid()
    ax_tern.scatter(xs, ys, zs)
    for i, author in enumerate(multilingual_authors):
        ax_tern.text(xs[i], ys[i], zs[i], author)
    ternary_file_name = "ternary_plot_%s.png" % re.sub(' ', '_', ego)
    plt.savefig(ternary_file_name)
    print("Figure saved to file %s" % ternary_file_name)
    plt.show()

# Currently only looking at de Groot and Christiaan Huyghens in detail, the rest get bunched together.
# Leeuwenhoek is skipped for now because of a different way of marking language, Descartes doesn't have any xml files at all
# Constantin Huyghens corpus also has the language in the expected place for only roughly 100 letters, so most of them are disregarded.
others_folders = ['ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/huyg001/', 'ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/barl001/', 'ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/beec002/', 'ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/nier005/', 'ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/swam001/']
corpuses = [('groot.hugo.1583-1645', 'Hugo de Groot', ['ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/groo001/']),
    ('huygens.christiaan.1629-1695', 'Christiaan Huyghens', ['ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/huyg003/']),
    ('foo', 'Others', others_folders)]
for ego_id, ego, folder in corpuses:
    letters = parse_transcriptions(folder)
    metadata, min_date, max_date, authors_list, lang_set = parse_metadata(letters)
    if 'foo' in ego_id:
        plot_timeline(ego, metadata, min_date, max_date, "correspondence of")
    else:
        # Split into sent and received for our main egos
        sent = [letter for letter in metadata if ego_id in letter['author']]
        received = [letter for letter in metadata if ego_id not in letter['author']]
        plot_timeline(ego, sent, min_date, max_date, "letters sent by")
        plot_timeline(ego, received, min_date, max_date, "letters received by")
    plot_authors(ego, metadata, authors_list)
