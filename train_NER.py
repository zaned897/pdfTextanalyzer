# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from __future__ import unicode_literals, print_function
import plac
import random
from pathlib import Path
import spacy
from tqdm import tqdm
import json
import random
import logging
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from sklearn.metrics import accuracy_score


# %%

def convert_dataturks_to_spacy(filename):

    with open(filename) as train_data:
	
        train = json.load(train_data)

    TRAIN_DATA = []

    for data in train:

	    ents = [tuple(entity) for entity in data['entities']]

	    TRAIN_DATA.append((data['content'],{'entities':ents}))
        
    return TRAIN_DATA


# %%
TRAIN_DATA = convert_dataturks_to_spacy('data/data_base/NER_DATA_TEST_FROM_SFILTER.json')
TRAIN_DATA = TRAIN_DATA[:][:-1]


# %%
## Ignore this until GPU is supported

import thinc_gpu_ops
print('thinc_gpu_ops?: ' , thinc_gpu_ops.AVAILABLE)

import spacy
print('spacy GPU ok?: ',spacy.prefer_gpu() and spacy.require_gpu())

null.tpl [markdown]
# ## First NER model ##

# %%
# First ner mdoel


import time
# check process time 
start_time = time.time()
# Optimal values: n_iter = 10, drop = 0.01

## Hyperparameters
model = None
output_dir=Path("./data/results/models")
n_iter= 100

## Load model

#load the model
if model is not None:
    nlp = spacy.load(model)  
    print("Loaded model '%s'" % model)
else:
    nlp = spacy.blank('en')  
    print("Created blank 'en' model")

#set up the pipeline
if 'ner' not in nlp.pipe_names:
    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner, last=True)
else:
    ner = nlp.get_pipe('ner')

## Disable PIPELINE
for _, annotations in TRAIN_DATA:
    for ent in annotations.get('entities'):
        #print(ent[2])
        ner.add_label(ent[2])

other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):  # only train NER
    optimizer = nlp.begin_training(device=0)
    for itn in range(n_iter):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in tqdm(TRAIN_DATA):
            nlp.update(
                [text],  
                [annotations],  
                drop=0.01,  
                sgd=optimizer,
                losses=losses)
        print(losses)
print('.'*50)
print("--- %s seconds ---" % (time.time() - start_time))
print('.'*50)

null.tpl [markdown]
# ## Save the re-trained model ##

# %%
if output_dir is not None:
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    print("Saved model to", output_dir)


