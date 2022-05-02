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

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_images(url):
    """
    Returns all image URLs on a single `url`
    """
    soup = bs(requests.get(url).content, "html.parser")
    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)
        # remove URLs like '/hsts-pixel.gif?c=3.2.5'
        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)
    return urls

def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))

import os
import sys
import requests
import simplejson as json

def connectionCheck():
	url = 'http://rxnav.nlm.nih.gov/REST/version'
	header = {'Accept': 'application/json'}
	getCheck = requests.get(url, headers=header)
	if getCheck.status_code != requests.codes.ok:
		response = "RXNorm server response error. Response code: %s" % getCheck.status_code
	else:
		response = "Connection check complete. RXNorm online. Response code: %s" % getCheck.status_code
	return response

def rxNorm(ndc):
	# ndc value coming from master.py
	# ndc = [array of ndc values]
	if ndc[0] is None:
		return {"rxcui": "", "rxtty": "", "rxstring": ""}
	else:
		# if internet or request throws an error, print out to check connection and exit
		try:
			baseurl = 'http://rxnav.nlm.nih.gov/REST/'

			# Searching RXNorm API, Search by identifier to find RxNorm concepts
			# http://rxnav.nlm.nih.gov/REST/rxcui?idtype=NDC&id=0591-2234-10
			# Set url parameters for searching RXNorm for SETID
			ndcSearch = 'rxcui?idtype=NDC&id='

			# Search RXNorm API, Return all properties for a concept
			rxPropSearch = 'rxcui/'
			rxttySearch = '/property?propName=TTY'
			rxstringSearch = '/property?propName=RxNorm%20Name'

			# Request RXNorm API to return json
			header = {'Accept': 'application/json'}
			def getTTY(rxCUI):
				# Search RXNorm again using RXCUI to return RXTTY & RXSTRING
				getTTY = requests.get(baseurl+rxPropSearch+rxCUI+rxttySearch, headers=header)

				ttyJSON = json.loads(getTTY.text, encoding="utf-8")

				return ttyJSON['propConceptGroup']['propConcept'][0]['propValue']

			def getSTRING(rxCUI):
				# Search RXNorm again using RXCUI to return RXTTY & RXSTRING
				getString = requests.get(baseurl+rxPropSearch+rxCUI+rxstringSearch, headers=header)
				stringJSON = json.loads(getString.text, encoding="utf-8")

				return stringJSON['propConceptGroup']['propConcept'][0]['propValue']

			# Search RXNorm using NDC code, return RXCUI id
			# ndc = [ndc1, ndc2, ... ]
			for item in ndc:
				getRXCUI = requests.get(baseurl+ndcSearch+item, headers=header)
				if getRXCUI.status_code != requests.codes.ok:
					print("RXNorm server response error. Response code: %s" % getRXCUI.status_code)
				rxcuiJSON = json.loads(getRXCUI.text, encoding="utf-8")
				# Check if first value in list returns a RXCUI, if not go to next value
				try:
					if rxcuiJSON['idGroup']['rxnormId']:
						rxCUI = rxcuiJSON['idGroup']['rxnormId'][0]
						rxTTY = getTTY(rxCUI)
						rxSTRING = getSTRING(rxCUI)
						return {"rxcui": rxCUI, "rxtty": rxTTY, "rxstring": rxSTRING}
				except:
					# if last item return null values
					if item == ndc[-1]:
						return {"rxcui": "", "rxtty": "", "rxstring": ""}
					pass
		except:
			sys.exit("RXNorm connection")












def parse_pillrximage_data(datasetpath):
    pilldf = pd.read_csv(datasetpath)

    temppilldf = pilldf[pilldf['name'].str.count('^[a-zA-Z\s]+[a-zA-Z]*\s\d+') > 0]

    temppilldf = temppilldf[temppilldf['name'].str.count('//*') == 0]
    temppilldf = temppilldf[temppilldf['name'].str.count('MG') > 0]

    temppilldf['name'] = temppilldf['name'].str.replace(r"\[.*?\]", "")
    temppilldf['name'] = temppilldf['name'].str.replace(r"\(.*?\)", "")

    temppilldf['name'] = temppilldf['name'].str.split('MG').str[0]
    temppilldf['name'] = temppilldf['name'].str.rstrip()
    temppilldf['name'] = temppilldf['name'].str.replace(" ", "_")
    classes = []

    for c in temppilldf['name'].unique():
        classes.append(c)
        #print(c)

    rootdatadir = 'C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillrximagenet\\train\\'



    for c in classes:
      try:
        os.mkdir(rootdatadir + c)
      except:
        pass
        #print(c, 'passed')

    for d in os.listdir(rootdatadir):

      resdf = temppilldf.loc[temppilldf['name'] == d]
      for img in list(resdf['RXBASE 300']):
        tempfilename = img.split('/')[-1]

        shutil.copy('C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillrximage\\'+img,'C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillrximagenet\\train\\' + d + '/' + tempfilename)

    return classes


def parse_pillbox_data(datasetpath,classes):
    for d in os.listdir(datasetpath):
        if '-' not in d:
            for c in classes:
                c = c.lower()

                flag = True
                ctemp = c.split('_')
                for ct in ctemp:

                    ct = ct.lower()
                    if ct in d:
                        pass
                    else:
                        flag = False
                        break
                if flag:
                    print(c)
                    print(d)


def parse_consumerdata(csvpath,classes):
    condf = pd.read_csv(csvpath)
    condf = condf[condf['Image'].str.count('(.JPG)|(.PNG)') > 0]
    condf = condf[condf['Name'].str.count('MG') > 0]
    consumer_classes = []
    for pill in list(condf['Name'].unique()):
        pillLower = pill.lower()
        for c in classes:
            c = c.lower()
            flag = True
            ctemp = c.split('_')
            for ct in ctemp:

                ct = ct.lower()
                if ct in pillLower:
                    pass
                else:
                    flag = False
                    break
            if flag:
                if pill not in consumer_classes:
                    consumer_classes.append(pill)


    condf = condf[condf['Name'].isin(consumer_classes)]

    return condf

def downsize_dataset(dir):
    root = 'C:\\Users\\Alejo\\.PyCharm2019.3\\config\\scratches\\consumer_all_images\\'
    for d in os.listdir(dir):
        print('resize ', d)
        try:
            dtemp = Image.open(root + d)
            dtemp = convert_resize_img(dtemp)
            print(dtemp.size)
            if '.png' in d:
                filetemp = d.replace('.png', '.JPG')
                os.remove(root + d)
                dtemp.save(root + filetemp)
            elif '.PNG' in d:
                filetemp = d.replace('.PNG', '.JPG')
                os.remove(root + d)
                dtemp.save(root + filetemp)
            elif '.jpg' in d or '.JPG' in d:
                os.remove(root + d)
                dtemp.save(root + d)
            else:
                break
        except:
            print('file corrupted removing: ', d)
            os.remove(root + d)



def convert_resize_img(img):
    img = img.convert('RGB')
    img = img.resize((300,225))
    return img


def get_images_from_database(df):
    root = 'C:\\Users\\Alejo\\.PyCharm2019.3\\config\\scratches\\consumer_all_images\\'
    skipped = []
    imagesinroot = os.listdir(root)
    alreadydwnld = []
    for imroot in imagesinroot:
        alreadydwnld.append(imroot.split('.')[0])
    print(alreadydwnld)
    rooturl = 'https://data.lhncbc.nlm.nih.gov/public/Pills/'
    i = 0
    total = len(list(df['Image']))

    for dir in list(df['Image']):
        print(dir.split('.')[0])
        dirfilename = dir.split('/')[-1]
        if dirfilename.split('.')[0] in alreadydwnld:
            print('image already in directory')
            i = i + 1
            pass
        else:
            print('saving image: ', i ,' out of ' , total )
            filename = dir.split('/')[-1]
            try:
                f = open('consumer_all_images/' + filename, 'wb')
                f.write(requests.get(rooturl + dir).content)
                f.close()
            except:
                skipped.append(dir)
                pass
            try:
                dtemp = Image.open('consumer_all_images/' + filename)
                dtemp = convert_resize_img(dtemp)
                if '.png' in filename:
                    filetemp = filename.replace('.png', '.JPG')
                    os.remove(root + filename)
                    dtemp.save(root + filetemp)
                    print(dtemp.size)
                elif '.PNG' in filename:
                    filetemp = filename.replace('.PNG', '.JPG')
                    os.remove(root + filename)
                    dtemp.save(root + filetemp)
                    print(dtemp.size)
                elif '.jpg' in filename or '.JPG' in filename:
                    os.remove(root + filename)
                    dtemp.save(root + filename)
                    print(dtemp.size)
            except:
                print('issue with image ', filename)
                print('skipped')
                skipped.append(dir)
                pass
            i = i + 1


def generate_con_train_folder(consumerdf,classes):
    root = 'C:\\Users\\Alejo\\.PyCharm2019.3\\config\\scratches\\train\\'
    all_img = 'C:\\Users\\Alejo\\.PyCharm2019.3\\config\\scratches\\consumer_all_images\\'
    print(classes)
    for c in classes:
      try:
        #print(root + c)
        os.mkdir(root + c)
      except:
        pass
    print(consumerdf.columns)
    for imgjpg in os.listdir(all_img):
        img = imgjpg.split('.')[0]
        consumerdf['Image'] = consumerdf['Image'].str.split('.').str[0]
        consumerdf['Image'] = consumerdf['Image'].str.split('/').str[-1]
        tempdf = consumerdf.loc[consumerdf['Image']==img]
        # print(img)
        # print(tempdf)

        if len(tempdf) > 1:
            print('error on image file ', img)
        else:
            clas = str(tempdf['Name'].values[0]).lower()
            class_num = 0
            for c in classes:
                if class_num > 1:
                    print('issue')
                    print('== ',c)
                    print('== ', img)
                    print('== ', clas)

                    class_num = 0
                flag = True
                cs = c.lower().split('_')
                for i in cs:
                    if i in clas:
                        pass
                    else:
                        flag = False
                        break
                if flag:
                    if re.sub('\D','',clas) in c:
                        class_num = 1+ class_num
                        print(c)
                        try:
                            shutil.copy(all_img + imgjpg,root + c + '\\' + imgjpg)
                        except:
                            print('already in file')


def fill_gaps_(dir1, dir2):

    emptydir1 = 0
    for d1 in os.listdir(dir1):
        total = 0
        for f in os.listdir(os.path.join(dir1, d1)):

            total = total + 1
            # if os.path.isfile(os.path.join(d1, f)):
            #     total = total + 1

        if total == 0:
            emptydir1 = emptydir1 + 1
        print(d1, ' has ', total, ' files')
    print('has ', emptydir1,' empty directories')



    for d2 in os.listdir(dir2):
        total = 0
        for f in os.listdir(os.path.join(dir2, d2)):
            total = total + 1
            # if os.path.isfile(os.path.join(d1, f)):
            #     total = total + 1
        if total !=0:
            #print(d2, ' has ', total, ' files')
            #print(total * 0.2)
            if total * 0.2 > 1.0:
                take_ratio = math.floor((0.8 * total))
                #print('take ratio ', take_ratio)
                for tr in os.listdir(os.path.join(dir2, d2)):
                    if take_ratio == 0:
                        break
                    else:
                        print('moving ',tr,' to train')
                        shutil.move(dir2 + d2 + '\\' + tr, dir1 + d2 + '\\' +tr)
                        take_ratio = take_ratio - 1


    emptydir2 = 0

    for d1 in os.listdir(dir1):
        total = 0
        for f in os.listdir(os.path.join(dir1, d1)):

            total = total + 1
            # if os.path.isfile(os.path.join(d1, f)):
            #     total = total + 1
        if total == 0:
            emptydir2 = emptydir2 + 1
        print(d1, ' has ', total, ' files')
    print('has ', emptydir2,' empty directories')

def remove_empty_dir(dir1,dir2):
    rm_list = []
    for d1 in os.listdir(dir1):
        total = 0
        for f in os.listdir(os.path.join(dir1, d1)):
            total = total + 1
        if total == 0:
            shutil.rmtree(dir1 + d1)
            shutil.rmtree(dir2 + d1)
# bad
#'/content/pillrximagenet/train/pantoprazole_20/B27FDKRV0W4W9EWN80EOSD8OQCE-BQK.JPG'



#classes = parse_pillrximage_data('C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillrximage\\table.csv')
#consumerdf =  parse_consumerdata('C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\consumer_dataset\\directory_consumer_grade_images.csv',classes)

#consumerdf.to_csv('C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\consumer_dataset\\consumer_data.csv')

#consumerdf = pd.read_csv('C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\consumer_dataset\\consumer_data.csv')

#downsize_dataset('C:\\Users\\Alejo\\.PyCharm2019.3\\config\\scratches\\consumer_all_images\\')

#fill_gaps_('C:\\Users\\Alejo\\.PyCharm2019.3\\config\\scratches\\train\\','C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillrximagenet\\train\\')
#get_images_from_database(consumerdf)


#generate_con_train_folder(consumerdf,classes)

# f = open('testimg.jpg','wb')
# f.write(requests.get('https://data.lhncbc.nlm.nih.gov/public/Pills/PillProjectDisc53/images/BZMJ5E3U9ZSM3EF93_1_Z2R1_T7YG22.JPG').content)
# f.close()

remove_empty_dir('C:\\Users\\Alejo\\.PyCharm2019.3\\config\\scratches\\train\\','C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillrximagenet\\train\\')

# dataTest = rxNorm(['66435-101-42', '66435-101-56', '66435-101-70', '66435-101-84', '66435-101-14', '66435-101-16', '66435-101-18'])
# print(dataTest)

# r = requests.get('https://data.lhncbc.nlm.nih.gov/public/Pills/index.html?_gl=1*o3zrvy*_ga*ODg0MjIwNTY3LjE2MzQ4NTkwMzg.*_ga_7147EPK006*MTY0OTE4NzY3NS44LjEuMTY0OTE4NzY3OS4w*_ga_P1FPTH9PL4*MTY0OTE4NzY3NS42LjEuMTY0OTE4NzY3OS4w')
#
# # Parse HTML Code
# soup = bs(r.text, 'html.parser')
# print(soup)
# # find all images in URL
# images = soup.find_all('tr')
# print(images)
# print(len(images))




# classes = parse_pillrximage_data('C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillrximage\\table.csv')
#
# parse_pillbox_data('C:\\Users\\Alejo\\Desktop\\medimagespring22\\Task01_BrainTumour\\MedDino\\pillbox_production_images_full_202008',classes)

