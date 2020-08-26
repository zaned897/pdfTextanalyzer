import ast # txt format
import numpy as np # math library

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


def search_rules (dictionary, rules):

    _,pos = map_words(dictionary)
    #radius =  .02 * np.sqrt(np.array(dictionary['top']).max()**2 + np.array(dictionary['left']).max()**2)
    radius = 300

    # convert in string, for search rules pourpuses
    new_sentences = ' '.join(dictionary['text']).upper()
    _tuple_rules = []
    _tuple_cords = []

    ## search for data points of interest
    # iterate througth each data point 
    for _, item in enumerate(rules):
        # search every combination of rules
        for i in range(len(rules[item])):
            # try to found complete rule
            try: 
                _pos = pos.index(new_sentences.index(rules[item][i]))
                ## !! se tiene que modificar
                _tuple_rules += [(rules[item][i],_pos)]
            
            # try to split the grammar rule
            except:
                # search word by word
                asociate_terms = rules[item][i].split(' ')
                
                if asociate_terms[0] in new_sentences:
                    # get the position
                    position = pos.index(new_sentences.index(asociate_terms[0]))+1
                    # get x, and y coords
                    coord_x = dictionary['left'][position]
                    coord_y = dictionary['top'][position]
                    # string for search
                    _aux = []
                    # search first match radius (i.e, DATE neighborhood -> date report, date loss, loss date, etc)
                    for j in range(len(dictionary['text'])):
                        # calculate the distance in neighborhood
                        dist_euc = np.sqrt((coord_x-dictionary['left'][j])**2 + (coord_y-dictionary['top'][j])**2)
                        if dist_euc <= radius:
                            _aux.append(dictionary['text'][j].upper())                                            
            
                    _aux_rules =rules[item][i].split(' ')
                  #  print(_aux)
                  #  print(_aux_rules)
                    if all(elem in _aux for elem in _aux_rules):
                        _tuple_rules += [(rules[item][i],pos.index(new_sentences.index(asociate_terms[0])))]

                else:
                    pass
    for i in range (len(_tuple_rules)):
        _tuple_cords += [(dictionary['left'][_tuple_rules[i][1]+1], dictionary['top'][_tuple_rules[i][1]+1])]
    return _tuple_cords