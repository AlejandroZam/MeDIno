import json
import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys
import os
import math
import re
import pandas as pd
import shutil
from PIL import Image
import urllib.request
import simplejson as json
import urllib
import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse



def kfold_split(ksplitfile,k):
    fileprefix = 'folds/pilltypeid_nih_sidelbls0.01_metric_5folds/base/pilltypeid_nih_sidelbls0.01_metric_5folds_'
    val_path = root + fileprefix + str(k) + '.csv'


    df = pd.read_csv(val_path)
    classes = df['label_code_id'].unique()
    classes.sort()
    print(classes)
    print(len(classes))
    # print(df)
    # print(df['label_code_id'].unique())
    #
    # print('here')

def dc_dr_split(root):
    fileprefix = 'all_labels.csv'
    labels = root + fileprefix
    df = pd.read_csv(labels)
    classes = df['label_code_id'].unique()
    classes.sort()
    print('classes = ',len(classes))
    datasetstruct = {}
    for c in classes:
        tempdf = df.copy()
        print('total len of images',len(tempdf))
        images_df = tempdf.loc[tempdf['label_code_id'] == c]
        print('class ', c)
        print('number of imgs in class ',len(images_df))
        # images_df_f = images_df.loc[images_df['is_front'] == True]
        # print('front images in class ',len(images_df_f))
        # datasetstruct[c] = images_df_f.image_path.values.tolist()
        datasetstruct[c] = images_df.image_path.values.tolist()

    return datasetstruct

    # print(classes)
    # print(len(classes))


def dc_train_dr_val_split():
    print('here')

def dr_train_dc_val_split():
    print('here')

def create_dataset_folder(src_dir,dest_dir,img_dict):


    for k,v in img_dict.items():
        print(k)
        print(v)


root = 'C:/Users/Alejo/Desktop/medimagespring22/Task01_BrainTumour/MedDino/ePillID_data/ePillID_data/'

# kfold_split(root,0)
src_dir = 'C:/Users/Alejo/Desktop/medimagespring22/Task01_BrainTumour/MedDino/ePILLID_DATASET'
dst_dir = 'C:/Users/Alejo/Desktop/medimagespring22/Task01_BrainTumour/MedDino/PillID_data/PillID_data'
img_dict = dc_dr_split(root)

create_dataset_folder('h','h',img_dict)