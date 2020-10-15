import os
import ast
from configobj import ConfigObj
import numpy as np
import copy
from cv2 import circle 
from cv2 import imread
from cv2 import imwrite
from cv2 import resize
from pdf2image import convert_from_path
import pytesseract as pt
from pytesseract import Output
from tensorflow.keras.utils import get_file
from gensim.models import KeyedVectors

def load_context_model():
    '''Load context model.
    Returns:
        model: A pre-trained model
    '''
    path = '/home/zned897/.keras/datasets/GoogleNews-vectors-negative300.bin.gz'
    model = KeyedVectors.load_word2vec_format(path, binary=True)
    return model


def update_files_in_path(root = './data/pdfs/', log_file = 'log_file.txt'):
    

    # get the actual files in path
    current = os.listdir(root)
    # get the log of the last modificated files
    
    try:
        _file = open(root + log_file, "r+")
        old = _file.read().splitlines()
        _file.close()
    except:
        _file = open(root + log_file, "w") 
        old = []
    
    # check modifications
    modified = list(set(current) - set(old)) + list(set(old) - set(current))
    #all_mod = list(set(old) - set(modified)) + modified

    # re-write the directory 
    with open(root + log_file, 'w') as f:
        for _file in current:
            f.write("%s\n" % _file)

    return modified

def transform_to_images_an_entire_folder(pdfs_folder = './data/pdfs/', images_folder = './data/images/', format = '.jpg', log_file = 'log_file.txt'):
    '''
    Transform all .pdf files into .jpg in specific folder ans store the images in default folder ./data/iamges/ .
    Args. 
        pdfs_folder: Folder path containing all pdf reports i. e., ./data/pdfs.
        images_folder: Folder path where results were stored.
        format: target format for images. 
    Returns.
        False if error in source path, or True if success
    '''

    # Validate pdf folder
    try:
        os.listdir(pdfs_folder)
    except:
        print("Error in path: " + pdfs_folder, 'It doesn exist or wrong path name')
        return False   

    # Create the target folder if it doesn't exists
    try:
        os.mkdir(images_folder)
    except FileExistsError:
        pass


    # for each .pdf modified, convert it into .jpg
    modified_files = update_files_in_path(root=pdfs_folder, log_file=log_file)

    for _file in modified_files: # process modified files
        if _file[-3:] == 'pdf': # process only pdf format images
            try:
                image_proto = convert_from_path(pdfs_folder + _file) # if the pdf file is not corrupted proceed
                
                if len(image_proto)>1:  # if there are several pages in the pdf file 
                    merged = np.array(image_proto[0])[:,:,0] # optimize process taking only a gray image
                    height = merged.shape[0]
                    width =  merged.shape[1]

                    for i in range(1, len(image_proto)):
                        y = np.array(image_proto[i])[:,:,0]
                        try:    
                            merged = np.append(merged, y, axis = 1)
                        except: 
                            try:
                                merged = np.append(merged,y.T,axis = 1)
                            except:                                 
                                y_resized = resize(y, dsize=(width,height))
                                merged = np.append(merged, y_resized, axis = 1)   
                    imwrite(images_folder + _file[:-4] + format, merged)
                    
                elif len(image_proto)==1:

                    imwrite(images_folder + _file[:-4] + format, np.array(image_proto[0]))

                else:
                    
                    print('Error in file: ' + images_folder + _file, len(image_proto[0]))
                    return False
            
                #Multiple images pdf
                #image_proto = convert_from_path(pdfs_folder  + _file)
                #[image.save(images_folder + _file[:-4] + str(page) + format) for page, image in enumerate(image_proto)]                            
            except:
                print('File: ' + str(_file) + ' delated or corrupted')
    return True

def transform_to_text_an_entire_folder(images_folder = './data/images/', text_folder = './data/txt/', save_string = False,log_file='log_file.txt'):

    '''
    Transform all images files supported into .txt as string or dictionary in specific folder and store it in a target folder
    Args. 
        images_folder: Folder path containing all pdf reports i. e., ./data/pdfs.
        text_folder: Folder path where results were stored.
        save_string: define the format in wich the OCR will save the image analisys
                     simple string if True, if False it will use the dict format i.e., dict['text'], dict['x'], dict['y'], etc. 
    Returns.
        False if error in source path, or True if success
    '''

    # Read soruce files
    try:
        os.listdir(images_folder)
    except:
        print("Error in path: " + images_folder, 'It doesn exist or wrong path name')
        return False   

    # Create the target folder if it doesn't exists
    try:
        os.mkdir(text_folder)
    except FileExistsError:
        pass

    modified = update_files_in_path(root=images_folder, log_file=log_file)
    # For each file with image format in path, convert it into .txt file
    for _file in modified:
        try:
            try: 
                pt.image_to_string(images_folder + _file)
                txt_file  = open(text_folder  + _file[:-3] + "txt", "w")
                if save_string:
                    txt_file.write(str(pt.image_to_string(images_folder + _file)))
                else:
                    txt_file.write(str(pt.image_to_data(images_folder + _file, output_type =Output.DICT)))
            except: 
                print('File: ' + images_folder + _file + ' not supported')
        except:
           print('File: ' + str(_file) + 'delated')
    return True

def spatial_filter(txt_dict, topics, report_type):
    '''Creates a list of words related by possotin related in , 
    Args:
        txt_dict (dict): Dictionary with raw txt info in pdf report
        topics (list): Topics list of the entities of interes
    Returns:
        all_candidates: List with text in same column and same row
    '''

    all_candidates = []
    for topic in range(len(topics)):
        (l, t, w, h) = (txt_dict['left'][topics[topic][2]],
                    txt_dict['top'][topics[topic][2]],
                    txt_dict['width'][topics[topic][2]],
                    txt_dict['height'][topics[topic][2]]
                    )
        vertical_candidates = []
        horizontal_candidates = []

        if report_type == 'LOSSRUN':
            for i in range(len(txt_dict['text'])):
                txt_left = txt_dict['left'][i]
                txt_top = txt_dict['top'][i]
                txt_text = txt_dict['text'][i]

                if (txt_left > l - w and txt_left < l + w and txt_top > t):
                    vertical_candidates.append(txt_text)
            
            for i in range(len(txt_dict['text'])):
                txt_left = txt_dict['left'][i]
                txt_top = txt_dict['top'][i]
                txt_text = txt_dict['text'][i]

                if (txt_top > t - h and txt_top < t + h and txt_left > l) and (txt_left-(l + w)<300):
                    horizontal_candidates.append(txt_text)

        elif report_type == 'NPDB':
                    for i in range(len(txt_dict['text'])):
                        txt_left = txt_dict['left'][i]
                        txt_top = txt_dict['top'][i]
                        txt_text = txt_dict['text'][i]

                        if (txt_top > t - h and txt_top < t + h and txt_left > l) and (txt_left-(l + w)<500):
                            horizontal_candidates.append(txt_text)
        elif report_type == 'EMAIL':

                    for i in range(len(txt_dict['text'])):
                        txt_left = txt_dict['left'][i]
                        txt_top = txt_dict['top'][i]
                        txt_text = txt_dict['text'][i]
                        
                        if (txt_top > t - h and txt_top < t + h and txt_left > l) and (txt_left-(l + w)<800):
                            horizontal_candidates.append(txt_text)
        else:

            for i in range(len(txt_dict['text'])):
                txt_left = txt_dict['left'][i]
                txt_top = txt_dict['top'][i]
                txt_text = txt_dict['text'][i]

                if (txt_left > l - w and txt_left < l + w and txt_top > t):
                    vertical_candidates.append(txt_text)
            
            for i in range(len(txt_dict['text'])):
                txt_left = txt_dict['left'][i]
                txt_top = txt_dict['top'][i]
                txt_text = txt_dict['text'][i]

                if (txt_top > t - h and txt_top < t + h and txt_left > l):
                    horizontal_candidates.append(txt_text)


        all_candidates +=  [vertical_candidates + horizontal_candidates]
    return all_candidates

def pre_proc(pdf_file, data_path, topic_file, image_format = '.png', text_format = '.txt'):
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
    image_file = PATH_image + pdf_file + '.png'
    txt_dict = read_dict(txt_file)
    template_rules = ConfigObj(topic_file)
    # Search topic in text raw dict
    j = search_rules(txt_dict,template_rules)
    print(image_file )
    _image_c = imread(image_file) 
    _image = imread(image_file) 

    for i in range(len(j)):
    # Box dimentions
        (l, t, w, h) = (txt_dict['left'][j[i][2]],
                    txt_dict['top'][j[i][2]],
                    txt_dict['width'][j[i][2]],
                    txt_dict['height'][j[i][2]]
                    )
        center = (l + np.uint8(w/2), t + np.uint8(h/2))
        color = (0, 0, 255)
        circle(_image, center, 8, color, -1)
    return txt_dict, j, _image, _image_c
    
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
                        
                    try:
                        _text_temp_dict[poss.index(sentence.index(rules[item][i]))+1] = '?' * len(_text_temp_dict[poss.index(sentence.index(rules[item][i]))+1])
                        rules_coords += [(item, rules[item][i],poss.index(sentence.index(rules[item][i]))+1, _temp_dict['left'][poss.index(sentence.index(rules[item][i]))+1], _temp_dict['top'][poss.index(sentence.index(rules[item][i]))+1])]
                        sentence = ' '.join(_text_temp_dict)
                    except:
                        break


            # if there is some part of the rule
            elif (rules[item][i].split(' ')[0] in sentence):
                
                asociate_terms = rules[item][i].split(' ')
                    
                while asociate_terms[0] in sentence:
                    try:
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
                    except:
                        break
            else:
                pass

    return rules_coords 


def is_report(image, txt):
    """
    Compare logos, and text content to determinate if the file is a loss report, email or NPDB document 

    Args.
        image(np.array): image in numpy format 
        text(dic): dictionary extracted from OCR stage

    Returns.
        String: email, NPDB, lossrun
    """


    content =' '.join(txt['text'])
    if ('FROM:'in content.upper()) and ('SENT:'in content.upper()) and ('@' in content.upper()):
        return ('EMAIL',ConfigObj('config/config_email_topics.ino'),ConfigObj('config/config_email_entities.ino'))
    elif 'NPDB' in content.upper():
        return ('NPDB', ConfigObj('config/config_npdb_topics.ino'),ConfigObj('config/config_npdb_entities.ino'))
    
    elif ('STATUS' in content.upper()) or ('STATUS' in content.upper()) or ('STUS' in content.upper()):
        return ('LOSSRUN', ConfigObj('config/config_lossrun_topics.ino'),ConfigObj('config/config_lossrun_entities.ino'))
    else:
        return 'any'
    