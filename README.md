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

#The data
TODO: add citation
The data used in this project consists of 20020 letters and some other texts from the corpuses of nine scientists
active in the Dutch republic in the 17th century. Some letters are available as transcriptions, others have been summarized.
They all have metadata about the sender and recipient as well as date, place and language use. This data is available in an XML format.
Here is an example of a ltter from Hugo de Groot's corpus (ckccRestored/1677705613221-Project_Circulation_of_Kn/original/data/corpus/data/groo001/groo001brie01_01.xml#L527-L545):
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

For this project, I am only looking at the metadata, that is the <interp> elements inside <interpGrp> elements in the xml files. I am also limiting the data only to those letters which have a known sender, approximate date, and listed language for the whole letter. Since this corpus is from several different institutions and presented in slightly different XML markup, I am limiting the data to those that are present in actual .xml files and using <interpGrp> tags (not <meta> tags) and have the language listed in an <interp> group and not as an attribute(?) for <div> elements inside the transcription. Anthoni van Leeuwenhoek's corpus (leeu027) is discarded since it seems to be from a bilingual Dutch-English collection of his letters with no indication as to what the original language of each letter was. While Constantijn Huyghens' (huyg001) letters do follow the format, most of them are discarded due to not having language info on a letter level. Descartes' corpus (desc004) is also discarded due to the structured data not being present in the archive.

This leaves us with Hugo de Groot, Christiaan Huyghens and Constantijn Huyghens. Which should be 18 233 letters in total according the the CKCC website https://ckcc.huygens.knaw.nl/?page_id=43
 After discarding letters which lack sender, language info or date, we are left with 11051 letters from 583 different senders in 9 different languages
