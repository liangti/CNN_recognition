'''
Created on Apr 24, 2017

@author: uuisafresh
'''

import shelve
import numpy as np
import tensorflow as tf
from cnn import cnn_recognition
from img_seg import *
from scipy import misc

def input_wrapper(f):
    image = misc.imread(f)
    sx,sy = image.shape
    diff = np.abs(sx-sy)

    sx,sy = image.shape
    image = np.pad(image,((sx//8,sx//8),(sy//8,sy//8)),'constant')
    if sx > sy:
        image = np.pad(image,((0,0),(diff//2,diff//2)),'constant')
    else:
        image = np.pad(image,((diff//2,diff//2),(0,0)),'constant')
    
#     image = dilation(image,disk(max(sx,sy)/28))
    image = misc.imresize(image,(28,28))
    if np.max(image) > 1:
        image = image/255.
    return image


def get_set(img_data, img_label,label_dict):
    count=0
    for i in range(len(img_data)):
        cur=np.zeros(41)
        if count==0:
            data=img_data[i].reshape(1,784)
            cur[label_dict[img_label[i]]]=1
            label=[cur]
            
        else:
            data=np.row_stack((data,img_data[i].reshape(1,784)))
            cur[label_dict[img_label[i]]]=1
            label=np.row_stack((label,cur))
        count+=1
#         if count>100: break
        print count
            
    print len(data), len(label)
    return data, label

def norm_result(arr):
    maxx=np.max(arr)
    minn=np.min(arr)
    for x in range(len(arr)):
        arr[x]=float(arr[x] - minn)/(maxx- minn)
    arr=arr/sum(arr)
    return arr

if __name__ == '__main__':
    flag='predict'
    img_data=shelve.open('img_data.db')
    
    if flag=='train':
        data_set,label_set=get_set(img_data['data'], img_data['label'], img_data['label_dict'])
         
        sess=tf.Session()
         
        clf=cnn_recognition(sess,flag='train')
        clf.network(data_set[0:3000], label_set[0:3000], train_size=3000)
    if flag=='predict':
        sess=tf.Session()
        
        clf=cnn_recognition(sess,flag='predict')
        file_path = 'SKMBT_36317040717363_eq7_=_75_115_545_593.png'
#         x, y, coord, b_box = segment(file_path)
#         recongize(coord, b_box, x, y)
        img=[input_wrapper(file_path)]
        target=['=']
        data, label=get_set(img,target,img_data['label_dict'])
        print label
        result=clf.network(data,label)
        print result
#         print y_conv
        arr = norm_result(np.asarray(result[0]))
        print arr
        
        print arr
        ans=np.argmax(arr)
        print ans,arr[ans],'first'
        arr[ans]=0
        print np.argmax(arr), arr[np.argmax(arr)],'second'
        print img_data['label_dict']
        
    if flag=='test':
        data_set,label_set=get_set(img_data['data'], img_data['label'], img_data['label_dict'])
        sess=tf.Session()
        clf=cnn_recognition(sess,flag='test')
        test_acc,result,cor=clf.network(data_set, label_set)
        name=img_data['name']
        n2i=img_data['label_dict']
        i2n=['' for i in range(len(n2i))]
        for key in n2i:
            i2n[n2i[key]]=key
        for i in range(len(result)):
            print name[i+3000],i2n[result[i]],i2n[cor[i]]
#     # clf=cnn_recognition(sess,flag='test')
#     # clf.network(data_set, label_set, train_size=3000)