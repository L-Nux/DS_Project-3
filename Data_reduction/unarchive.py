#!/usr/bin/env python
# coding: utf-8

# In[5]:


from zipfile import *
import os
 
#where to unzip
zip_out = '/Users/marinakozevnikova/Desktop/Uni2021/Project/3dm/'
# location of a file
file_path = '/Users/marinakozevnikova/Desktop/Uni2021/Project/20211007_3dim_rohdaten.zip'
 
if os.path.isfile(file_path):
    print("FILE path name:", file_path) 
    try :        
        with ZipFile (file_path, 'r') as zip_file :
            file_name_list = zip_file.namelist ()
            for file_name in file_name_list :
                if '11_15_Dortmund_Duisburg' in file_name :             
                    print ("IN ZIP -->>  ",file_path)
                    print ("FILE NAME-->", file_name)
                    try :
                        zip_file.extract(file_name, zip_out)                       
                    
                    except RuntimeError:
                        continue
                        
    except BadZipfile :
        print ("Bad Zip File", zip_file)
    


# In[9]:


from zipfile import ZipFile
import subprocess, sys

def Unzip(zipFile, destinationDirectory):
    try:
        with ZipFile('/Users/marinakozevnikova/Desktop/Uni2021/Project/20211007_3dim_rohdaten.zip', 'r') as zipObj:
            listOfFileNames = zipObject.namelist()
            for fileName in listOfFileNames:
            # Extract all the contents of zip file in different directory
                if fileName.startswith('11_15_Dortmund_Duisburg'):
                    zipObject.extract(fileName, '/Users/marinakozevnikova/Desktop/Uni2021/Project/3dm/')
                    print('All the python files are extracted')
            
    except:
        print("An exception occurred extracting with Python ZipFile library.")
        print("Attempting to extract using 7zip")
        subprocess.Popen(["7z", "e", f"{zipFile}", f"-o{destinationDirectory}", "-y"])
                              
                  


# In[ ]:





# In[ ]:




