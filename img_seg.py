'''
Created on Apr 24, 2017

@author: uuisafresh
'''
import numpy as np
from skimage import data, filters, segmentation, measure, morphology, color
from PIL import Image

#segment the image according the connected regions 
def segment(file_path):

    #binarize the image
    im_arr = binarize(file_path)
    bw = im_arr.copy()

    #bw = morphology.closing(image > thresh, morphology.square(3))
    
    #labels connected regions
    label_image = measure.label(im_arr)
    #display_region(bw, label_image, im_arr)
    
    #coordinate list (row, col) of the connected region
    coord = {}
    #bounding box (min_row, min_col, max_row, max_col)
    b_box = []

    for region in measure.regionprops(label_image): 

        #ignore the small regions
        if region.area < 9:
            continue

        #get the min and max x-axis
        x_min = region.bbox[1]
        x_max = region.bbox[3]
        
        b_box.append([x_min, x_max])

        #get the cood list of all connected regions
        coord[tuple([x_min, x_max])] = region.coords
        print coord[tuple([x_min, x_max])]
    return len(bw), len(bw[0]), coord, b_box

#binarize the image
def binarize(file_path):
    
    im = Image.open(file_path)
    image = np.array(im.convert('L'))
       
    for x in range(len(image)):
        for y in range(len(image[0])):
            image[x, y] = 255 if image[x, y] > 50 else 0

    return image


def judge(i_min, i_max, j_min, j_max):
    if i_min<=j_min and i_max>=j_max:
        return True
    ins_min=max(i_min,j_min)
    ins_max=min(i_max,j_max)
#     com_min=min(i_min,j_min)
#     com_max=max(i_max,j_max)
#     print (ins_max-ins_min)/float(i_max-i_min)
#     print (ins_max-ins_min)/float(j_max-j_min)
    if ins_min<ins_max:
        if ((ins_max-ins_min)/float(i_max-i_min)+(ins_max-ins_min)/float(j_max-j_min))/2>=0.7:
            return True
    return False
#merge the overlapping areas                        
def merge(intervals):
#     sort the intervals of x-axis
    keys = []
    merge = []
    for i in range(len(intervals)):
        merge.append(tuple(intervals[i]))
        for j in range(len(intervals)):
            if i==j: continue
            if judge(intervals[i][0],intervals[i][1],intervals[j][0],intervals[j][1]):
                merge.append(tuple(intervals[j]))
        if len(merge)<=3 and len(merge)>1:
#             print merge
            keys.append(merge)
        merge=[]


    return keys

#recongize connected regions of the image
#input: coordinates, bounding box, areas of the whole image
def recongize(coord, b_box, x, y):

    merge_keys = merge(b_box)
    
    for m_k in merge_keys:
#         print m_k
        nm = np.zeros((x, y))
        for co in m_k:
            temp = coord[co]
            nm = connected_arr(nm, temp)

        new_im = Image.fromarray(nm)
        new_im.show()



def recog_merge(coord, b_box, x, y):
    merge_keys = merge(b_box)
    merge_group=[]
    print len(merge_keys)
    for m_k in merge_keys:
        nm = np.zeros((x, y))
        img_group=[]
        key_group=[]
        for co in m_k:
            cur = np.zeros((x, y))
            temp = coord[co]
            nm = connected_arr(nm, temp)
            cur = connected_arr(cur, temp)
#             img_group.append(cur)
            key_group.append(co)
        img_group.append(nm)
        print len(img_group)
        merge_group.append([img_group,key_group])
    return merge_group
#get the array of a connected region


def connected_arr(nm, con_arr):

    for ordinate in con_arr:
        nm[ordinate[0]][ordinate[1]]= 255
        
    return nm

#helper function for checking whether an image is segmented correctly

#show the segmented arrays in image form
def array2Pic(arr):

    for a in arr:
        new_im = Image.fromarray(a)
        new_im.show()

#output all images after merge
def output_img(coord, x, y):
    img_group=[]
    for c in coord:
        nm = np.zeros((x, y))
        temp = coord[c]
        nm = connected_arr(nm, temp)
        img_group.append(nm)
    return img_group
# name=['SKMBT_36317040717260_eq13.png','SKMBT_36317040717260_eq33_pi_68_109_479_530.png','SKMBT_36317040717260_eq6.png','SKMBT_36317040717260_eq6_=_85_109_596_630.png']
# file_path = name[1]
# x, y, coord, b_box = segment(file_path)
# recongize(coord, b_box, x, y)

#array2Pic(res)
