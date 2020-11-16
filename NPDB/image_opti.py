# %% load dependencies
import numpy as np 
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from sklearn.metrics import mean_squared_error
import time
# %% load data 

# check the processing time

start_time = time.time()
pdf_file = 'data/AI NPDB.pdf'
images = convert_from_path(pdf_file, grayscale=True, size=(60, 60))
    
print('*** Elapsed time:', time.time() - start_time)
# %% check time 
image_base = np.array(images[23])
image_test = np.array(images[6])

plt.figure(figsize=(17, 15))
plt.subplot(2, 1, 1), plt.imshow(image_base)
plt.subplot(2, 1, 2), plt.imshow(image_test)

print(mean_squared_error(image_test, image_base))

# %%
