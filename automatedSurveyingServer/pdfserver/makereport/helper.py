import os
import numpy as np
import cv2
from glob import glob
import tensorflow as tf
from PIL import Image
import math
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

def mask_parse(mask):
    mask = np.squeeze(mask)
    mask = [mask, mask, mask]
    mask = np.transpose(mask, (1, 2, 0))
    return mask

def read_i(path):
    x = cv2.imread(path, cv2.IMREAD_COLOR)
    
    x = cv2.resize(x, (256, 256))
    x = x/255.0
    return x

def predictSettle(p,i,h):
    model = tf.keras.models.load_model("/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/models/modelSettle.h5")
    x = read_i(f'/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/static/{p}00{i}.jpg')
    y_pred = model.predict(np.expand_dims(x, axis=0))[0] > 0.5
    out = mask_parse(y_pred) * 255.0
    count = np.count_nonzero(out)/3

    cv2.imwrite(f"/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/static/resultSettle{p}00{i}.jpg", out)
    area = float((math.tan(math.pi/5))*2*h)**2
    print (f"area : {area} m^2")
    areaPerPixel = area/(256**2)
    print (areaPerPixel)
    return ({"areacover":areaPerPixel*count,"area":area,"areaPerPixel":areaPerPixel,"height":h,"imageid":f"{p}00{i}","resultid":f"resultSettle{p}00{i}.jpg"})

def predictWater(p,i,h):
    modelPath = os.path.abspath("models")+"/modelWater.h5"
    model = tf.keras.models.load_model("/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/models/modelWater.h5")
    x = read_i(f'/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/static/{p}00{i}.jpg')
    y_pred = model.predict(np.expand_dims(x, axis=0))[0] > 0.5
    out = mask_parse(y_pred) * 255.0
    count = np.count_nonzero(out)/3

    cv2.imwrite(f"/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/static/resultWater{p}00{i}.jpg", out)
    area = float((math.tan(math.pi/5))*2*h)**2
    print (f"area : {area} m^2")
    areaPerPixel = area/(256**2)
    print (areaPerPixel)
    return ({"areacover":areaPerPixel*count,"area":area,"areaPerPixel":areaPerPixel,"height":h,"imageid":f"{p}00{i}","resultid":f"resultWater{p}00{i}.jpg"})

def predictNDVI(p,imageNumber,h):
    img = Image.open(f'/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/static/{p}00{imageNumber}.jpg')
    imgF = np.asarray(img.resize((300,300)))
    imgFinal = np.array((imgF/255),dtype=np.float32)
    ndviMatrix = np.zeros((300,300),dtype=np.float32)
    for i in range(300):
        for j in range(300):
            deno = imgFinal[i][j][1] + imgFinal[i][j][0] - imgFinal[i][j][2]
            if (deno != 0):
                ndviMatrix[i][j] = round(((imgFinal[i][j][1] - imgFinal[i][j][0])/(deno)),6)
            else:
                ndviMatrix[i][j] = 2

    ndviImage = np.zeros((300,300,3),dtype='uint8')
    for i in range(300):
        for j in range(300):
            ind = ndviMatrix[i][j]
            if (ind >=-1 and ind<=1):
                ndviImage[i][j]=[
                            int ((-127.5*ind) + 127.5),
                            int ((127.5*ind) + 127.5),
                            0]
            else:
                ndviImage[i][j]=[200,200,200]

    # Generating the R-G Colourmap
    red = np.linspace(1,0,256)
    green = np.linspace(0,1,256)
    blue = np.zeros((256),dtype='float')
    alpha = np.ones((256),dtype='float')
    CMap = list(zip(red,green,blue,alpha))
    color = np.array(CMap)
    newMap = ListedColormap(color)
    
    # Making The final Image
    fig, (ax1, ax2) = plt.subplots(figsize=(16, 5), ncols=2)
    pos = ax1.imshow(ndviImage/255, cmap=newMap, interpolation='none', vmin=-1,vmax=1)
    fig.colorbar(pos, ax=ax1)
    ax2.imshow(imgFinal)

    # saving the image
    fig.savefig(f"/home/jkhan01/Desktop/automatedSurveyingServer/pdfserver/makereport/static/resultNDVI{p}00{imageNumber}.jpg")
    txt = ''
    if np.average(ndviMatrix) > 0:
        txt = "vegetative land recognised"  
    else:
        txt = "No significant vegetaion found"
    count = 0
    for i in range(300):
        for j in range(300):
            if ndviMatrix[i][j] > 0 and ndviMatrix[i][j]<=1:  
                count += 1
    area = float((math.tan(math.pi/5))*2*h)**2
    print (f"area : {area} m^2")
    areaPerPixel = area/(256**2)
    print (areaPerPixel)
    return ({"areacover":areaPerPixel*count,"area":area,"areaPerPixel":areaPerPixel,"height":h,"imageid":f"{p}00{imageNumber}","resultid":f"resultNDVI{p}00{imageNumber}.jpg"})


if __name__ == '__main__':
    print (predictSettle(1,1,20))
    # print (predictWater(20))
