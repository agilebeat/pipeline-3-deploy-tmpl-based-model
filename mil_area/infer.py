# try:
#   import unzip_requirements
# except ImportError:
#   pass


import json
import boto3
import os
import base64
import io

import cv2 
import numpy as np



#--- load featured color values 



def decode_base64_to_cv2(img_b64):
    img = base64.urlsafe_b64decode(img_b64)
    img_io = io.BytesIO(img)
    img_np = np.frombuffer(img_io.read(), dtype=np.uint8)
    img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    pic = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
    return pic  # 256x256x3 


#--- Classify
templates = './template/'

def classify_template_match(templates, img_cv2, threshold=0.9):
    prediction = 1
    templates = [os.path.join(templates, template) for template in os.listdir(templates)]
    
    n_th_template = 0
    for tmpl in templates:
        template = cv2.imread(tmpl, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_cv2, template, cv2.TM_CCOEFF_NORMED)
        thresh = threshold
        
        loc = np.where(res >= thresh)
        if (len(loc[0]) == 0):
            n_th_template += 1
        else:
            break
        
    if (n_th_template == len(templates)):
        prediction = 0
    return prediction


def inferHandler(event, context):
    body_txt = event['body']
    body_json = json.loads(body_txt)
    z = body_json['z'] 
    x = body_json['x']
    y = body_json['y']
    tile_base64 = body_json['tile_base64']
    img_cv2 = decode_base64_to_cv2(tile_base64)

    predictions = classify_template_match(templates, img_cv2, threshold=0.9)


    if predictions == 0:
        dic = False
    else:
        dic = True


    response = {
        "statusCode": 200,
        "headers": {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        "body": json.dumps({'FeatureClass': dic})
    }
    
    return response


