import os
import numpy as np
import cv2
from glob import glob
import tensorflow as tf
import math
class MLClass():
    def mask_parse(self,mask):
        mask = np.squeeze(mask)
        mask = [mask, mask, mask]
        mask = np.transpose(mask, (1, 2, 0))
        return mask

    def read_i(self,path):
        x = cv2.imread(path, cv2.IMREAD_COLOR)
        
        x = cv2.resize(x, (256, 256))
        x = x/255.0
        return x

    def predictSettle(self,p,i, h):
        model = tf.keras.models.load_model(os.path.abspath("/models/modelSettle.h5"))
        x = self.read_i('/home/jkhan01/Desktop/automatedSurveying/static/'+str(p)+'/images/'+str(i)+'.jpeg')
        y_pred = model.predict(np.expand_dims(x, axis=0))[0] > 0.5
        out = self.mask_parse(y_pred) * 255.0
        count = np.count_non_zero(out)
        return (((math.tan(math.pi/5))*2*h*count)/256)

    def predictWater(self,p,i, h):
        model = tf.keras.models.load_model(os.path.abspath("/models/modelWater.h5"))
        x = self.read_i('/home/jkhan01/Desktop/automatedSurveying/static/'+str(p)+'/images/'+str(i)+'.jpeg')
        y_pred = model.predict(np.expand_dims(x, axis=0))[0] > 0.5
        out = self.mask_parse(y_pred) * 255.0
        count = np.count_non_zero(out)
        return (((math.tan(math.pi/5))*2*h*count)/256)
class genReport():
    def __init__(self,heightData,pid,pname):
        self.heightData = heightData
        self.pname = pname
        self.pid = pid
        self.settle = 0.0
        self.water = 0.0
    
    def computeSettle(self):
        obj = MLClass()
        for i in self.heightData:
            self.settle += obj.predictSettle(self.pid,i,self.heightData[i])
        return self.settle
    
    def computeWater(self):
        obj = MLClass()
        for i in self.heightData:
            self.water += obj.predictWater(self.pid,i,self.heightData[i])
        return self.settle
    def generate_md(self):
        
        count = 0
        for i in self.heightData:
            count+=1
        base_md = "# Survey Report for Project: " + self.pname +"\n" + "## Total Number of Study Images: " + str(count) +"\n" + "## Vegetation Reports:"
        
        for i in self.heightData:
            base_md += "<br><img src='/home/jkhan01/Desktop/automatedSurveying/static/" + self.pid +f"images/{i}.jpeg' style='width:300px;height:300px'>" 
        base_md += "\n"+"## Settlement Area: "+"\n" + ">> " + "350 sq.m" + "\n"
        base_md += "## Water Area: " + "\n" + ">> "+"100 sq.m"
        return base_md

