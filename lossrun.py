import ast # txt format
import numpy as np # math library
import copy

def read_dict(txt_file_path):
    ## Read txt file as dict more data available (i.e., position, size and      level info)
    # open file 
    txt_file = open(txt_file_path,'r')

    # read data in txt file
    txt_raw = txt_file.read()

    # read the content as dictionary 
    txt_as_dict  = ast.literal_eval(txt_raw)
    
    # close the file
    txt_file.close()
    
    return txt_as_dict

## Extract features from dictionary data, as mass center, deviation, text size, claims, and others

# take the list of multiple txt files as input
def extract_statistic_featrues(list_of_paths_of_txt_files):
    
    # get the  number of params to meassure
    
    # create empty variables for mean, std, etc according files size 
    mean_x, mean_y, std_x, std_y, size_x, size_y = [],[],[],[],[],[]
    #
    words_number, no_claims, max_levels, level_average = [],[],[],[]
    
    # get the number of files to extract 
    files = len(list_of_paths_of_txt_files)
    
    # extract each data
    for i in range(files):

        # convert the txt data to dict form
        data_dict = read_dict(list_of_paths_of_txt_files[i])

        # get the mean features. LEFT = x, TOP = y
        mean_x.append(np.mean(data_dict['left']))
        mean_y.append(np.mean(data_dict['top']))
        std_x.append(np.std(data_dict['left']))
        std_y.append(np.std(data_dict['top']))
    
        # get the pdf text size
        size_x.append(np.max(data_dict['left']) - np.min(data_dict['left']))
        size_y.append(np.max(data_dict['top']) - np.min(data_dict['top']))

        # get the words numbers 
        words_number.append(len(data_dict['text']))

        # no claims in report? 
        no_claims.append(('NO CLAIM' or 'NO LOSS') in ' '.join(data_dict['text']))

        # max of levels
        max_levels.append(np.max(data_dict['level']))

        # level average
        level_average.append(np.mean(data_dict['level']))

    return np.array([mean_x] + [mean_y] + [std_x] + [std_y] + [size_x] + [size_y] + [words_number] + [no_claims] + [max_levels] + [level_average])

def map_words(txt_dict):
    elements = len(txt_dict['text'])
    x = np.zeros(shape= (elements,1),dtype = int)
    y = np.zeros(shape= (elements,1), dtype = int)
    pos = []
    string_result = ''
    for i in range (elements):
        string_result+= txt_dict['text'][i] + ' '
        pos.append(len(string_result))
        x[i] = txt_dict['left'][i]
        y[i] = txt_dict['top'][i]

    return string_result.upper(),pos


def search_rules(dictionary, rules):
    
    radius = 300
    # map words possitions in text list
    _, poss = map_words(dictionary)

    # Deep copy dictionary 
    _temp_dict = copy.deepcopy(dictionary)


    # convert to uppercase
    _temp_dict['text']= [_temp_dict['text'][i].upper() for i in range(len(_temp_dict['text']))]

    # create the sentences
    sentence = ' '.join(_temp_dict['text'])

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
                        
                    _temp_dict['text'][poss.index(sentence.index(rules[item][i]))+1] = '?' * len(_temp_dict['text'][poss.index(sentence.index(rules[item][i]))+1])
                    rules_coords += [(rules[item][i], _temp_dict['left'][poss.index(sentence.index(rules[item][i]))+1], _temp_dict['top'][poss.index(sentence.index(rules[item][i]))+1])]
                    sentence = ' '.join(_temp_dict['text'])


            # if there is some part of the rule
            elif (rules[item][i].split(' ')[0] in sentence):
                
                asociate_terms = rules[item][i].split(' ')
                    
                while asociate_terms[0] in sentence:
                    
                    position = poss.index(sentence.index(asociate_terms[0]))+1
                    coord_x = _temp_dict['left'][position]
                    coord_y = _temp_dict['top'][position]
                    _aux = []
                    for j in range(len(_temp_dict['text'])):
                        dist_euc = np.sqrt((coord_x - _temp_dict['left'][j])**2 + (coord_y - _temp_dict['top'][j])**2)
                       
                        if dist_euc <= radius:
                            _aux.append(_temp_dict['text'][j])
                                    
                    

                    if all(elem in _aux for elem in asociate_terms):
                    
                        _temp_dict['text'][poss.index(sentence.index(asociate_terms[0]))+1] = '}' * len(_temp_dict['text'][poss.index(sentence.index(asociate_terms[0]))+1])
                        rules_coords  += [(asociate_terms[0], _temp_dict['left'][poss.index(sentence.index(asociate_terms[0]))+1] , _temp_dict['top'][poss.index(sentence.index(asociate_terms[0]))+1])]
                        sentence = ' '.join(_temp_dict['text'])
                       
                    else:
                        break
            else:
                pass

    return rules_coords 