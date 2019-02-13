# HABLA Lexical Resources
This is a code to align equivalents groups of discourse markers between Spanish and Portuguese based on the translation of individual markers. In this repository, they are also available the discourse marker lexicons which along with a number of heuristics can support the task of automatically detecting and correcting discourse marker errors made by native Spanish speakers in their academic writing in Portuguese. These resources integrate a module of the HABLA (Hispanic speakers acquiring a Base of Academic Language) project, an academic writing support tool in Portuguese for native Spanish speakers.

To test the code, run the following command:

```cluster_discourse_markers.py -e ../input/spanishDiscourseMarkers_HABLA.txt -d ../input/portugueseDM_HABLA.txt -m ../input/top10_PT2SP_translations.txt```

The parameters are:
spanishDiscourseMarkers_HABLA.txt: list of Spanish discourse markers
portugueseDM_HABLA.txt: list of Portuguese discourse markers
top10_PT2SP_translations.txt: discourse markers translation between Spanish and Portugues, obtained with Moses.


# Citation

```
Sepúlveda-Torres L., Sanches Duran M. and Aluísio S. (forthcoming, 2019) Automatic Detection and Correction 
of Discourse Marker Errors Made by Spanish Native Speakers in Portuguese Academic Writing. 
Language Resources and Evaluation Journal.
```
