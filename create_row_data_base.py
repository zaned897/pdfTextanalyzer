"""
Create a raw image for all txt files
"""
#%%
import os 
import ast
import lossrun


# %%


from tensorflow.keras.utils import get_file

try:
    path = get_file('GoogleNews-vectors-negative300.bin.gz', 
        origin='https://s3.amazonaws.com/dl4j-distribution/'+'GoogleNews-vectors-negative300.bin.gz')
except:
    print('Error downloading')
    raise
    
print(path)


# %%
print(path)
import gensim

# Not that the path below refers to a location on my hard drive.
# You should download GoogleNews Vectors (see suggested software above)
model = gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)

# %%
#w = model['insured']
#print(w)
string = "Carrier:  Line of  Policy Num retention Status Description Open By email  submitted  dated 3-Apr-17  Verna Bennett  wheelchair  onto the  was taken  Infirmary  fracture/dislocation Open Letter from  Patient's  advising  malpractice  been filed  connection  occurred  fell from  being offloaded    Certain Underwriters at Lloyds - Certain    Loss Report prepared for A-MMED Ambulance Inc., DBA A-Med Carrier:"
model.doesnt_match(string.split())
#print(string.split())

#%%
model.most_similar('insurer')