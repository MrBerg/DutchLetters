#Dutch letters: a final project for the Computational literacy course
###By Jonas Berg

##Requirements to replicate
Software used:
* Python 3 (I'm using 3.9.13)
* matplotlib 3.8.2
* mpltern 1.0.2
* numpy 1.26.2

Older versions of python, matplotlib, mpltern and numpy probably work as well.

The required libraries are hopefully easily just by running `pip install -r requirements.txt` from this folder
or maybe `python3 -m pip install -r requirements.txt` to ensure you are actually using python3

To get access to the data, download the CKCC data from [their gitlab](https://gitlab.huc.knaw.nl/ckcc/corpus) or [the archived data at DANS](https://doi.org/10.17026/dans-xfd-n8y5) and extract it into this folder. I downloaded revision 8bff13f390e5b32bb331c86854f9c85e97438482 of the Gitlab repo, as downloading from version 2 of the archive was not possible when starting this work, but it may be functional again with version 3. After extraction you should have a `ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data` folder with subfolders for the corpuses, wherein there are txt files and xml files containing the letter transcriptions and metadata.

To run the program, just run `python3 main.py` from this folder, most of the output will be to stdout
and the figures will be in popup windows. You need to close the window to have the program move forward. The figures are also automatically saved to separate .png files.

##Research questions
This project tries to answer two questions:
1. How does the popularity of different languages vary for letters during the studied time period, and why?
2. Which languages do different kinds of authors use?

While Latin was the predominant language for learned communication in the Middle Ages, French would start to replace it especially for international and diplomatic use during the Early Modern period. Scientific writing would continue to be done mainly in Latin for this whole period, but vernacular languages also gained more and more use for domestic communication. By looking at the senders of letters and the language they write in, we can gain a glimpse at what languages they expected the receiver to understand and which language they considered the correct one for their particular letter, be it due to subject matter and established terminology or their own level of language proficiency.

##The data
The data used is officially to be cited as HuygensING-CKCC, 2011, "Project Circulation of Knowledge and learned practices in the 17th-century Dutch Republic. A web-based Humanities Collaboratory on Correspondences (Geleerdenbrieven) - archived version d.d. 2013-07-23", https://doi.org/10.17026/dans-xfd-n8y5, DANS Data Station Social Sciences and Humanities, V3, UNF:6:M3CZThdwpPeElXlaFE/RLQ== [fileUNF]

The dataset comes from [the CKCC project](https://ckcc.huygens.knaw.nl/) and consists of 20020 letters and some other texts from the corpuses of nine scientists
active in the Dutch republic in the 17th century. Some letters are available as transcriptions, others have been summarized.
They all have metadata about the sender and recipient as well as date, place and language use. This data is available in a TEI-conformant XML format.
Here is [an example](ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/groo001/groo001brie01_01.xml#L527-L545) of a letter from Hugo de Groot's corpus:
```
<!-- BOI -->
<div type="chapter" subtype="artifact">
<interpGrp>
<interp type="id" value="0007"/>
<interp type="date" value="1599"/>
<interp type="sender" value="meursius.johannes.1579-1639"/>
<interp type="senderloc" value="?"/>
<interp type="recipient" value="groot.hugo.1583-1645"/>
<interp type="recipientloc" value="?"/>
<interp type="language" value="la"/>
</interpGrp>
<head type="ed" id="a0007">7. [<date>1599</date>]. Van Joh. Meursius<note n="3"><seg type="source">Gedr. Io. Meursi Exercitatt. critic. I p. 244 (1599)</seg>, vóór de Notae in Plauti Truculentum.</note>.</head>
<div type="opener">
<p><persName key="meursius.johannes.1579-1639">Ioannes Meursius</persName> <persName key="groot.hugo.1583-1645">Hugeiano Grotio</persName> S.D.</p>
</div>
<p><hi rend="i">Odi puerum praecoci sapientia</hi>, aiebat ille<note n="4">Apuleius, Apol. 85.</note>; sed eo dicto, mi <persName key="groot.hugo.1583-1645">Groti</persName>, nihil censeo ineptius. Cur enim? Quippe <hi rend="i">generosioris arboris etiam planta cum fructu est</hi><note n="5">Quintilianus, Inst. or. VIII, 3, 76.</note>, quod Quintiliano iuvene dictitabatur.
Sed aurem vellit <persName>Cato</persName>, qui ‘senilem iuventam signum esse praematurae mortis’ pronuntiat<note n="6">Plinius, Nat. Hist. VII, 52.</note>. Quod utinam falsum? exemplis enim et experientia comprobatum, non diurnare hoc hominum genus. Dolendum certe: et quod de Caesare<note n="7">S. Aurelius Victor, Epitome 28.</note> olim dictum, ‘non nasci eum debere, aut Reip. non tam cito eripi’, idem de praecocibus et praestantissimis istis ingeniis videtur; quibus si ad frugem pervenire daretur, quanto usui Reip. erant futura? Tua caussa hoc dico, cui in ipsa fere pueritia tam praeclare sapere contigit, ut <hi rend="i">μελλέϕηβος</hi> in ingenii et eruditionis admirationem cunctos erexeris. Cave autem te efferas, aut ames nimis propter haec: quin Dei potius in te beneficentiam agnosce, illique ut gratus sis sedule labora. Gratus autem eris - vide quam sollicitus sit hic affectus, quem non contemnes - si dona, quae tibi largiter suppeditavit, nominis ipsius sanctissimi solius gloriae, Reique publicae utilitati impendere studebis. Quod nisi facis, infelix es, immo nihili. Hoc cogita, et me ama: atque haec ad Plauti Truculentum examina.</p>
</div>
<!-- EOI -->
```

##What I did with the data
For this project, I am only looking at the metadata, that is the <interp> elements inside <interpGrp> elements in the XML files. I am also limiting the data only to those letters which have a known sender, approximate date, and listed language for the whole letter. Since this corpus is from several different institutions and presented in slightly different XML markup, I am limiting the data to those that are present in actual .xml files and using <interpGrp> tags (not <meta> tags) and have the language listed in an <interp> group and not as an attribute for <div> elements inside the transcriptions. I identify letters in the XML by searching for <div> elements of the subtype "artifact". Another subtype "replaced_artifact" may also refer to letters, possibly lost or not available or not transcribed, but those elements are excluded for now to make the parsing easier.

Anthoni van Leeuwenhoek's corpus (leeu027) is discarded since it seems to be from a bilingual Dutch-English collection of his letters with no indication as to what the original language of each letter was. While Constantijn Huyghens' (huyg001) letters do follow the expected XML format, most of them are discarded due to not having language info on a letter level. Descartes' corpus (desc004) is also discarded due to the structured XML data not being present in the archive.

This leaves us with Hugo de Groot's, Christiaan Huyghens' and Constantijn Huyghens' corpuses, which should be 18 233 letters in total according to [the CKCC website](https://ckcc.huygens.knaw.nl/?page_id=43)

I parse all the XML files and combine them into one under a common root, after which I go through the children of all <interpGrp> tags to extract senders, dates and languages. I discard all letters where any of these values are marked as missing. The letters are dated with a varied precision, I only extract the year and in case of a multi-year period (presumably mostly two), the first year.

After discarding letters which lack sender, language info or date, we are left with 11051 letters from 583 different senders in 9 different languages.

For the timeline of language variance, I simply plot the amount of letters in Latin, French, Dutch, and German per year in my extracted list of years.

I then go through all smaller languages (not Latin, French, Dutch) and print all senders with letters in that language together with a count of their letters in that language and the total amount of letters they have sent.

After that I go through the amount of letters they have sent in Latin, French and Dutch and calculate the relative proportions to create a ternary scatterplot and a backup 3d scatterplot that is easier to rotate and zoom in on. I only looked at letters in these three languages, since those are the three languages that are most present in the CKCC corpus and get their own columns in the project's [table on language variation](https://ckcc.huygens.knaw.nl/?page_id=43). I also print out the top 100 most prolific authors in these languages in text format before I limit the data to only contain those 84 authors who write in more than one of these three languages. I also print out that list of "multilingual" authors

##Analysis
The [timeline](timeline.png) shows that Latin is the predominant language of letters in the first half of the 17th century, while French takes over in the second half. Dutch is also relatively popular in the 1610s-1640s. The predominance of French is perhaps due to France's rise as a superpower, being at its height during the reign of Louis XIV (r. 1643–1715, personal rule 1661-1715). The persecution of the Protestant Huguenots during his reign probably also caused some of them to emigrate to the Dutch republic or petition their brothers in faith to help them, in French.

The timeline also shows that letters in German are almost exclusively in the same period of ca 1630-1650 from where a huge portion of de Groot's corpus comes. This could possibly be related to the Thirty Years War' (1618-1648) raging on in the German states at that time. The German material is predominantly from Georg Keller (1589-1652) who was the secretary to the Swedish envoy to Hamburg, Johan Adler Salvius (according to [this note](https://www.dbnl.org/tekst/groo001brie11_01/groo001brie11_01_0304.php#4829T)), so it seems possible. Salvius is the second-most prolific German writer in this subset.

The [3d scatterplot](3d_scatter.png) and [ternary plot](ternary_plot.png) show many authors writing in varying amounts of French and Latin exclusively, and some using Latin and Dutch exclusively, not very many using French and Dutch exclusively. Very few people are using all three languages, among them Hugo de Groot, Constantijn Huyghens (1596-1687) and Christiaan Huyghens who are the people whose corpuses are used. Other interesting trilingual letter-writers are Constantijn Huyghens (1628-1697), Queen Kristina of Sweden, Johannes Uytenbogaert (1557-1644) and Johan Brosterhuyzen (1596-1650). Further research could go into this correspondence for a close reading to find out whether all these letters are written by the senders or by a secretary, and what their contents are per language.

##Potential biases and problems
The dataset is dominated by Hugo de Groot's correspondence. This problem also existed in the complete CKCC corpus, but there Constantijn Huyghens also contributed with almost as many letters as de Groot, and my subset of data additionally excludes all the small corpuses. Trying to analyse 17th century use of language by counting only one language per letter is not very representative of the actual practice at the time, where one letter could contain paragraphs or sentences or even sentence fragments in many different languages. There is a case to be made for including German in the "major languages" I look at in detail since roughly 200 letters in my subset are in German. However I excluded it because 1) the CKCC project lumps it together with other rarer languages in the corpus, and 2) trying to do a 4d scatterplot was beyond my ability. Most of the interesting results regarding German and other minor languages can be attained just by looking at the top lists per language which is present in the output.

It should be pointed out that the CKCC corpus consists of scientists well-known enough to have archived their correspondence and receive later publications of it. It cannot be said to be representative of all Dutch letter-writers of the period, not to mention the people they were in contact with.

It is entirely possible that I am misunderstanding how some of the XML files are structured and that my filtering of letters to analyze is discarding interesting categories of letters. Since I developed the program starting with de Groot and looking mostly into the structure of his corpus, and I got to a point where I could analyse almost all of his letters, I have just assumed that the remaining corpuses behave mostly the same. Since most of the non-epistolary material is concentrated to Constantijn Huyghens' corpus and I exclude most of it, I assume I am not including a lot of e.g. minutes of a meeting that the CKCC project mentions.

I am blindly trusting the CKCC corpus data to be correct, though [the project website](https://ckcc.huygens.knaw.nl/?page_id=43) does mention many problems it encountered with the dataset. Presumably many of them were fixed during the course of the project, such as the different spelling variations of names.

No proper statistical analysis of the timeline is done, no correlation analysis or interpolation. This is mostly due to lack of time. I am also not doing any proper cluster analysis or heatmaps or the like for the scatterplots, just judging by eye, so any results should be taken as extremely preliminary.

The scatterplots are littered with the labels for each writer. This is a bad compromise where the main point is trying to make the writers identifiable. I could have made them anonymous points and judge them as a nameless mass, or picked a subset of them, maybe the top 20 writers, but I do not know if that would be more representative or more misleading. Another alternative would have been to use some other plotting library and make the labels appear only when the mouse cursor hovers over a point, but this was not done due to time constraints.

The analysis is pretty surface level and does not refer to previous research nor does it go into detail on how to classify "monolingual", "bilingual" or "trilingual" authors into interesting national/societal groups.

The output could be saved in eg. a csv file instead of directly in stdout for re-use and more data analysis.
