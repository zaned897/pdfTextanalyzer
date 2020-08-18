# pdfTextanalyzer
pdf text extractor, text analyzed by NTLK, testing for gpt3 as last stage

# Requirements
- AI for Loss Runs and NPDB

# Hypothesis 
The Loss Runs Reports provide enough contextual clues to enable a grammar-driven approach for Information Extraction. 

# Discovery phase
- Get comprehensive sample
- Define Data Points of interest
- Create ontology 
- Define architecture: are we populating a relational database? 
- Understand the status of the current development (OCR), what else has been developed?

# Development phase
- Get directory of files
- Parse file names in directory (maintain parsing rules)
- Get relevant PDFs
- OCR PDF → Status of Tesseract. 
- NER model (contextual) by vendor. Maintain rules per vendor. Gazetteers & Grammars to be applied. Tokenize->POS tag->supervised tagging->chunking with grammars->Information Extraction

# Risks
The reports are presented in a wide range of formats. This will affect the scalability of this project if there aren’t enough training report models to handle the wide range of formats.

# Solution:
A grammar-driven approach can quickly accommodate new formats vs training a model.  
 


>Loss Runs Bank Reports
>National Practitioner Bank reports
>Text & Images

# Summary
This goal is to create an automated data entry program for loss runs and National Practitioner Data Bank reports. These reports are all in PDF format as seen in the sample reports provided. Some of these PDFs are text-based while other PDFs present the reports with images. Using text transcription and optical character recognition (OCR), the information from the PDF has to be converted to computer-readable text (raw text files). From there, keywords can be extracted from the text files after using a named-entity recognition (NER) model to first label the text. This process involves training the NER model with pre-labeled sample reports to properly label new reports at a high success rate.
 
# Current Status
As of right now, converting the PDFs to raw text using text transcription and optical character recognition has been completed with a high success rate using Tesseract (the open-source OCR engine). We are still exploring options for the natural language processing (NLP) component of this project to label the text, though we are leaning towards using the NER model. There are a few functions we have created that have returned desired names and dates from the text file with this approach and unsupervised learning (without using a training sample). However, it should be noted that the success rates of these functions have not been measured.
 
# Future Work
Most of the work for this project will be put into entity analysis of the text files using NLP concepts. We are currently using the software library spaCy to approach this problem, though it may be required later on to use TensorFlow instead given the wide range of information that is provided in these reports. We will move onto performance analysis once the NLP model is completed and trained. The final step will be creating a user-interface platform where reports can be inputted and automated data entries can be outputted.
 
# Potential Shortcomings
Inconsistent formats.
The reports are presented in a wide range of formats. This will affect the scalability of this project if there aren’t enough training report models to handle the wide range of formats.
 
# PDF Quality
There is a direct correlation between the quality of the PDFs with the performance of the Tesseract which impacts the OCR process.
 
#Next Steps
-Acquire complete dataset to further our analysis and test our approach.
-Parse file names to identify loss runs
-Process loss runs

>Loss RunPeople:
>Ari
>Eric
>Chen


# Development status
## Prerequisites
### Linux
- Check version python 3
```sh
$ python3 --version
```
- The software need python 3.6 or higher 
- In case of not having the version install python version 3.6
```sh
$ sudo apt-get update
$ sudo apt-get install python3.6
```
- Download pdfTex analyzer repository on GitHub [here](https://github.com/zaned897/pdfTextanalyzer)
- Install virtualenv
```sh
$ sudo apt install python3-virtualenv
```
- Install tesseract
```sh
$ sudo apt install tesseract-ocr
```

- Create virtualenv
```sh
$ virtualenv -p /usr/bin/python3 "name"
```
- Run virtualenv

```sh
$ cd "name"
$ source bin/activate
```
- Install requirements
```sh
$ pip install -r requirements.txt
```
- Stop virtualenv
```sh
$ deactivate
```
### Windows
- Check version python 3
```sh
$ python3 --version
```
- The software need python 3.6 or higher 
- In case of not having the version install python version 3.6 [here](https://www.python.org/downloads/windows/)
- Add python 3 in the PATH
- Download pdfTex analyzer repository on GitHub [here](https://github.com/zaned897/pdfTextanalyzer)
- Install virtualenv
```sh
$ pip install virtualenv
```
- Install tesseract [here](https://github.com/UB-Mannheim/tesseract/wiki)
- Add tesseract in the PATH
- Create virtualenv
```sh
$ virtualenv "name"
```
- Run virtualenv

```sh
$ cd "name"
$ Scripts\activate
```
- Install requirements
```sh
$ pip install -r requirements.txt
```
- Stop virtualenv
```sh
$ Scripts/deactivate
```
## Methodology
# Context
![flowchart](https://github.com/zaned897/pdfTextanalyzer/blob/master/data/results/Flowchart.png)

![flowchart](https://github.com/zaned897/pdfTextanalyzer/blob/master/data/results/test.png)

