import ast # txt format
import numpy as np # math library
import copy
import cv2
import os
from configobj import ConfigObj
from tensorflow.keras.utils import get_file
from gensim.models import KeyedVectors
import spacy
from spacy import displacy
# load entity model

def load_context_model():
    '''Load context model.

    Returns:
        model: A pre-trained model
    '''
    path = '/home/zned897/.keras/datasets/GoogleNews-vectors-negative300.bin.gz'
    model = KeyedVectors.load_word2vec_format(path, binary=True)
    return model

def spatial_filter(txt_dict, topics):
    '''Creates a spatial filter, 

    Args:
        txt_dict (dict): Dictionary with raw txt info in pdf report
        topics (list): Topics rules

    Returns:
        all_candidates: List with text in same column and same row
    '''
    all_candidates = []
    for i in range(len(topics)):
        (l, t, w, h) = (txt_dict['left'][topics[i][2]],
                    txt_dict['top'][topics[i][2]],
                    txt_dict['width'][topics[i][2]],
                    txt_dict['height'][topics[i][2]]
                    )
        for i in range(len(txt_dict['text'])):
            txt_left = txt_dict['left'][i]
            txt_top = txt_dict['top'][i]
            txt_text = txt_dict['text'][i]
            if (txt_left > l - w and txt_left < l + w and txt_top > t):
                all_candidates.append(txt_text)
            if (txt_top > t - h and txt_top < t + h and txt_left > l):
                all_candidates.append(txt_text)
    return all_candidates

def pre_proc(pdf_file, data_path, topic_file):
    '''Read raw txt info in pdf report, text file and image then search a topic and create a circle for each target

    Args:
        pdf_file (str): The PDF file name
        data_path (str): The data path same level than txt and images
        topic_file (str): The data path of topics

    Returns:
        txt_dict (dict): A dictinary with file content
        _image_c (numpy.ndarray): Image with drawn circle
        _image (numpy.ndarray): Original image
        j (list): List with search topic in text raw dict

    '''
    PATH_txt = os.path.join('.', data_path, 'txt','')
    PATH_image = os.path.join('.', data_path, 'images','')
    txt_file = PATH_txt + pdf_file + '.txt'
    image_file = PATH_image + pdf_file + '.jpg'
    txt_dict = read_dict(txt_file)
    template_rules = ConfigObj(topic_file)
    # Search topic in text raw dict
    j = search_rules(txt_dict,template_rules)
    _image_c = cv2.imread(image_file) 
    _image = cv2.imread(image_file) 

    for i in range(len(j)):
    # Box dimentions
        (l, t, w, h) = (txt_dict['left'][j[i][2]],
                    txt_dict['top'][j[i][2]],
                    txt_dict['width'][j[i][2]],
                    txt_dict['height'][j[i][2]]
                    )
        center = (l + np.uint8(w/2), t + np.uint8(h/2))
        color = (0, 0, 255)
        cv2.circle(_image_c, center, 8, color, -1)
    return txt_dict, _image_c, _image, j
    
def read_dict(txt_file_path):
    """ Read txt file as dictionary
    Parameters
    ----------
    txt_file_path : str
        The file location
    Returns
    -------
    dict
        a dictionary of file content
    """
    txt_file = open(txt_file_path,'r')
    txt_raw = txt_file.read()
    txt_as_dict  = ast.literal_eval(txt_raw)
    txt_file.close()
    return txt_as_dict

def extract_statistic_featrues(list_of_paths_of_txt_files):
    '''Extract features from dictionary data, as mass center, deviation, text size, claims, and others

    Args:
        list_of_paths_of_txt_files (list): Take the list of multiple txt files as input

    Returns:
        np.array: 
    '''
    # create empty variables for mean, std, etc according files size 
    mean_x, mean_y, std_x, std_y, size_x, size_y = [],[],[],[],[],[]
    words_number, no_claims, max_levels, level_average = [],[],[],[]
    # Number of files to extract 
    files = len(list_of_paths_of_txt_files)
    # Extract data
    for i in range(files):
        data_dict = read_dict(list_of_paths_of_txt_files[i])

        left = data_dict['left']
        top = data_dict['top']
        text = data_dict['text']
        level = data_dict['level']

        mean_x.append(np.mean(left))
        mean_y.append(np.mean(top))
        std_x.append(np.std(left))
        std_y.append(np.std(top))
    
        # PDF text size
        size_x.append(np.max(left) - np.min(left))
        size_y.append(np.max(top) - np.min(top))

        words_number.append(len(text))
        no_claims.append(('NO CLAIM' or 'NO LOSS') in ' '.join(text))
        max_levels.append(np.max(level))
        level_average.append(np.mean(level))

    return np.array([mean_x] + [mean_y] + [std_x] + [std_y] + [size_x] + [size_y] + [words_number] + [no_claims] + [max_levels] + [level_average])

def map_words(txt_dict):
    '''Match items of words in text dictionary

    Args:
        txt_dict (dict): Dictionary with raw txt info in pdf report

    Returns:
        string_result (str): String transformed to uppercase
        position (list): List with position of word
    '''
    elements = len(txt_dict['text'])
    x = y = np.zeros(shape = (elements, 1), dtype = int)
    position = []
    string_result = ''
    for i in range (elements):
        string_result += txt_dict['text'][i] + ' '
        position.append(len(string_result))
        x[i] = txt_dict['left'][i]
        y[i] = txt_dict['top'][i]
    return string_result.upper(), position


def search_rules(dictionary, rules):
    # most be modified
    radius = 200

    # map words possitions in text list
    _, poss = map_words(dictionary)

    # Deep copy dictionary 
    _temp_dict = copy.deepcopy(dictionary)

    _text_temp_dict = _temp_dict['text']

    # convert to uppercase
    _text_temp_dict = [_text_temp_dict[i].upper() for i in range(len(_text_temp_dict))]

    # create the sentences
    sentence = ' '.join(_text_temp_dict)

    # define the list for results 
    rules_coords = []
    
    # iterate trhougth rules
    for _, item  in enumerate(rules):

        for i in range(len(rules[item])):

            # if there is the entire rule in the text
            if rules[item][i] in sentence:

                # process while rule is in the text
                while rules[item][i] in sentence: 
                    # text 
                        
                    _text_temp_dict[poss.index(sentence.index(rules[item][i]))+1] = '?' * len(_text_temp_dict[poss.index(sentence.index(rules[item][i]))+1])
                    rules_coords += [(item, rules[item][i],poss.index(sentence.index(rules[item][i]))+1, _temp_dict['left'][poss.index(sentence.index(rules[item][i]))+1], _temp_dict['top'][poss.index(sentence.index(rules[item][i]))+1])]
                    sentence = ' '.join(_text_temp_dict)


            # if there is some part of the rule
            elif (rules[item][i].split(' ')[0] in sentence):
                
                asociate_terms = rules[item][i].split(' ')
                    
                while asociate_terms[0] in sentence:
                    position = poss.index(sentence.index(asociate_terms[0]))+1
                    coord_x = _temp_dict['left'][position]
                    coord_y = _temp_dict['top'][position]
                    _aux = []
                    for j in range(len(_text_temp_dict)):
                        dist_euc = np.sqrt((coord_x - _temp_dict['left'][j])**2 + (coord_y - _temp_dict['top'][j])**2)
                       
                        if dist_euc <= radius:
                            _aux.append(_text_temp_dict[j])
                                    
                    

                    if all(elem in _aux for elem in asociate_terms):
                    
                        _text_temp_dict[poss.index(sentence.index(asociate_terms[0]))+1] = '}' * len(_text_temp_dict[poss.index(sentence.index(asociate_terms[0]))+1])
                        rules_coords  += [(item, asociate_terms[0], poss.index(sentence.index(asociate_terms[0]))+1, _temp_dict['left'][poss.index(sentence.index(asociate_terms[0]))+1] , _temp_dict['top'][poss.index(sentence.index(asociate_terms[0]))+1])]
                        sentence = ' '.join(_text_temp_dict)
                       
                    else:
                        break
            else:
                pass

    return rules_coords 