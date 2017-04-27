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

def input_wrapper(f,arr=None):
    if arr==None:
        image = misc.imread(f)
    else:
        image=arr
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


def get_set(img_data,img_label=None,label_dict=None):
    count=0
    for i in range(len(img_data)):
        cur=np.zeros(41)
        if count==0:
            data=img_data[i].reshape(1,784)
            if img_label!=None:
                cur[label_dict[img_label[i]]]=1
                label=[cur]
            
        else:
            data=np.row_stack((data,img_data[i].reshape(1,784)))
            if img_label!=None:
                cur[label_dict[img_label[i]]]=1
                label=np.row_stack((label,cur))
        count+=1
#         if count>100: break
        print count
            
#     print len(data), len(label)
    if img_label!=None:
        return data, label
    else:
        return data

def norm_result(arr):
    maxx=np.max(arr)
    minn=np.min(arr)
    for x in range(len(arr)):
        arr[x]=float(arr[x] - minn)/(maxx- minn)
    arr=arr/sum(arr)
    return arr

if __name__ == '__main__':
    flag='recognize'
    img_data=shelve.open('img_data.db')
    name=img_data['name']
    n2i=img_data['label_dict']
    i2n=img_data['index']
    with tf.Session() as sess:
        if flag=='train':
            data_set,label_set=get_set(img_data['data'], img_data['label'], img_data['label_dict'])
             
             
            clf=cnn_recognition(sess,flag='train')
            clf.network(data_set[0:3000], label_set[0:3000], train_size=3000)
        if flag=='predict':
            
            clf=cnn_recognition(sess,flag='predict')
            file_path = 'SKMBT_36317040717260_eq33_pi_68_109_479_530.png'
    #         x, y, coord, b_box = segment(file_path)
    #         recongize(coord, b_box, x, y)
            img=[input_wrapper(file_path)]
            target=['pi']
            data, label=get_set(img,target,img_data['label_dict'])
            print label
            result=clf.network(data,label)
            print result
    #         print y_conv
            print sum(result[0])
            arr = norm_result(np.asarray(result[0]))
            print arr
            
            print arr
            ans=np.argmax(arr)
            
            print ans,arr[ans],'first'
            print img_data['label_dict']
            
        if flag=='test':
            data_set,label_set=get_set(img_data['data'], img_data['label'], img_data['label_dict'])
    
            clf=cnn_recognition(sess,flag='test')
            clf.init_network()
            test_acc,result,cor=clf.network(data_set, label_set)
            
            i2n=['' for i in range(len(n2i))]
            for key in n2i:
                i2n[n2i[key]]=key
            for i in range(len(result)):
                print name[i+3000],i2n[result[i]],i2n[cor[i]]
                
        if flag=='recognize':
            name=['SKMBT_36317040717260_eq13.png','SKMBT_36317040717260_eq33_pi_68_109_479_530.png','SKMBT_36317040717260_eq6.png','SKMBT_36317040717260_eq6_=_85_109_596_630.png']
            file_path=name[1]
    
            x, y, coord, b_box=segment(file_path)
            merge_group=recog_merge(coord, b_box, x, y)
            clf=cnn_recognition(sess,flag='predict')
            prior=['pi','=','i','div']
            for m in merge_group:
                img=[input_wrapper(f=None,arr=m[0][0])]
                data=get_set(img)
                predict=clf.network(data,save=True)
                result=i2n[np.argmax(predict)]
                if result in prior:
                    key_set=m[1]
                    for k in range(1,len(key_set)):
                        print len(coord[key_set[0]]),'1',type(coord[key_set[0]])
                        print len(coord[key_set[k]]),'2'
    #                     coord[key_set[0]]=coord[key_set[0]]+coord[key_set[k]]
                        coord[key_set[0]]=np.row_stack((coord[key_set[0]],coord[key_set[k]]))
                        print len(coord[key_set[0]]),'3'
            img_group=output_img(coord, x, y)
            for i in img_group:
                img=[input_wrapper(f=None,arr=i)]
                data=get_set(img)
                predict=clf.network(data)
                result=i2n[np.argmax(predict)]
                print result
#     # clf=cnn_recognition(sess,flag='test')
#     # clf.network(data_set, label_set, train_size=3000)