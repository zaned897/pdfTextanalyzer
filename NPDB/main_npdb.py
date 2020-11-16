# %% load dependencies 
from pdf2image import convert_from_path
import pytesseract as pt
from pytesseract import Output
import time
import concurrent.futures
import lossrun
from configobj import ConfigObj
import spacy
import re
import numpy as np
from datetime import datetime

# %% DATA READ AND PROCESS 
# time it
start = time.time()

# Transform entire pdf format to text
PATH = 'data/NPDB - with loss.pdf'
images = convert_from_path(PATH, dpi=100)  # conversion


# extract txt in image
def extract_text(image):
    return pt.image_to_data(image, output_type=Output.DICT)


# save a dict for each page 
dictionaries = []

# process each image width multi-threads
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(extract_text, image) for image in images]
    for result in concurrent.futures.as_completed(results):
        dictionaries.append(result.result())

#
print('Process time: ')
print(time.time() - start)

# % GROUP CLAIMS IN REPORTS
all_dcn_list = []

# get all the DCN number in NPDB files
for _dict in dictionaries:
    if 'DCN:' in _dict['text']:
        all_dcn_list.append(_dict['text'][_dict['text'].index('DCN:') + 1])

# remove repeated values
dcn_list = list(dict.fromkeys(all_dcn_list))

claims = []
# haga busqueda e incerción
for dcn in dcn_list:
    aux = {'level': [], 'page_num': [], 'block_num': [], 'par_num': [], 'line_num': [], 'word_num': [], 'left': [],
           'top': [], 'width': [], 'height': [], 'conf': [], 'text': []}
    i = 0
    for _dict in dictionaries:
        if dcn in _dict['text']:
            if _dict['top'][_dict['text'].index(dcn)] < 100:
                _dict['top'] = list(np.array(_dict['top']) + (2200 * i))
                i += 1
                for key in _dict.keys():
                    aux[key] = aux[key] + _dict[key]

    claims.append(aux)

# % LOAD MODEL AND EXTRACT CONTEXTUAL DATA
# load contextual model

manual_flag = True
if not manual_flag:
    print('loading NPDB NER model...')
    nlp = spacy.load('./config/NPDB_ner_model')

topic_conf = ConfigObj('config/config_npdb_topics.ino')
Topics = ConfigObj('./config/config_npdb_entites.ino')
regexp_act = r"\b[A-Z][A-Z]+\b"
# search for topics and entities
for dcn, claim in enumerate(claims):

    suspects = lossrun.search_rules(claim, topic_conf)
    spatial_filter = lossrun.spatial_filter(claim, suspects, 'NPDB')
    spatial_filter_topics = len(spatial_filter)

    # extract data
    pract_name, ref_number, ent_name, paid_by, total_pract, outcome, init_act, act_basis = [], [], [], [], [], [], [], []
    # get the entities for each sptatial relation

    proc_date = [datetime(1900, 1, 1)]
    event_date = [datetime(1900, 1, 1)]
    paid_date = [datetime(1900, 1, 1)]
    relevant = True

    for topic in range(spatial_filter_topics):
        # clean the sentece
        # spatial_filter[topic] = list(dict.fromkeys(spatial_filter[topic]))
        sentence = ' '.join(spatial_filter[topic])
        sentence = re.sub('\s+', ' ', sentence)
        doc = nlp(sentence)
        # print(sentence)
        for ent in doc.ents:
            if suspects[topic][0] == 'pract_name':
                if ent.label_ in Topics['pract_name']:
                    pract_name.append(ent.text)
            if suspects[topic][0] == 'ref_number':
                if ent.label_ in Topics['ref_number']:
                    ref_number.append(ent.text)
            if suspects[topic][0] == 'proc_date':
                if ent.label_ in Topics['proc_date']:
                    try:
                        proc_date.append(datetime.strptime(ent.text, '%m/%d/%Y'))
                    except:
                        pass
            if suspects[topic][0] == 'paid_date':
                if ent.label_ in Topics['paid_date']:
                    try:
                        paid_date.append(datetime.strptime(ent.text, '%m/%d/%Y'))
                    except:
                        pass
            if suspects[topic][0] == 'event_date':
                if ent.label_ in Topics['event_date']:
                    try:
                        event_date.append(datetime.strptime(ent.text, '%m/%d/%Y'))
                    except:
                        pass
            if suspects[topic][0] == 'ent_name':
                if ent.label_ in Topics['ent_name']:
                    ent_name.append(ent.text)
            if suspects[topic][0] == 'paid_by':
                if ent.label_ in Topics['ent_name']:
                    paid_by.append(ent.text)
            if suspects[topic][0] == 'total_pract':
                if ent.label_ in Topics['total_pract']:
                    total_pract.append(ent.text)

        if suspects[topic][0] == 'outcome':
            outcome.append(sentence)
        if suspects[topic][0] == 'init_act':
            aux = re.findall(regexp_act, sentence)
            sentence = ' '.join(aux)
            init_act.append(sentence) if sentence is not '' else None
        if suspects[topic][0] == 'act_basis':
            aux = re.findall(regexp_act, sentence)
            sentence = ' '.join(aux)
            act_basis.append(sentence) if sentence is not '' else None
        if suspects[topic][0] == 'relevant':
            relevant = False

    pract_name = str(pract_name)[1:-1]
    ref_number = str(ref_number)[1:-1]
    # proc_date = str(proc_date)[1:-1]
    # paid_date =  str(paid_date)[1:-1]
    # event_date = str(event_date)[1:-1]
    ent_name = str(ent_name)[1:-1]
    paid_by = str(paid_by)[1:-1]
    total_pract = str(total_pract)[1:-1] + '0'
    total_pract = int(float(re.sub("[$|,|'|*]", '', total_pract)))
    outcome = str(outcome)[1:-1]
    init_act = str(init_act)[1:-1]

    print('.' * 50)
    print('pract_name:' + pract_name)
    # print('ref_number:' + str(ref_number))
    print('proc_date:' + str(max(proc_date)))
    print('paid_date:' + str(max(paid_date)))
    print('event_date:' + str(max(event_date)))
    print('paid_by:' + str(paid_by))
    print('total_pract:' + str(total_pract))
    print('outcome:' + str(outcome))
    print('ent_name:' + str(ent_name))
    print('init_act:' + str(init_act))
    print('relevance:' + str(relevant))
    print('DCN:' + dcn_list[dcn])

    # lossrun_models.npdbRecord(process_date = max(proc_date),
    #                      practitioner_name = pract_name,
    #                      action_initial = init_act,                  
    #                      action_basis = act_basis, 
    #                      entity_name = ent_name,
    #                      payment_date = max(paid_date), 
    #                      payment_total_amount = total_pract,
    #                      event_day = max(event_date), 
    #                      event_outcome = outcome,
    #                      event_paid_by = dcn_list[dcn])

#    for i in range (len(spatial_filter)):
#        sentence  = ' '.join(spatial_filter[i])
#        sentence = re.sub('\s+',' ', sentence)
#        doc = nlp(sentence)   
#        print('search: ' + suspects[i][0] + ' in: ' + sentence)
#        for ent in doc.ents:
#            print(ent.label_)
#    print('*'*100)
