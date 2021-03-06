#!/usr/bin/python2
#coding:UTF-8
#无需存储bottleneck
import pathlib
import random
import os
import numpy as np
#从训练集里随机获取一个batch的数据
#假如有BATCH的大小为BATCH_SIZE。则每次随机在训练集里选择一个类，然后随机选择一个数据
#next_batch函数获得的batch的最终形式为张量形式
#返回是一个batch的bottleneck和对应groundtruth
#CACHE_DIR='./cache'
INPUT_DATA='/extra_store/Y-npy/'
def next_batch_bottleneck(sess, n_classes, video_lists, how_many, category, npy_data_tensor, bottleneck_tensor):
    i=0
    while(True):#循环BATCH_SIZE次
	label_index = random.randrange(n_classes)#随机选一类
	label_name = list(video_lists.keys())[label_index]#获得这个类名
	video_index = random.randrange(65536)#为什么是65536


	#计算bottleneck的值!!!!!
	bottleneck,flag = get_or_create_bottleneck(sess, video_lists, label_name, video_index, category, npy_data_tensor, bottleneck_tensor)
        if flag==False:
            #print('format is not suitable,pass!----%s'%label_name)
            continue
	#生成这个类对应的groundtruth编码（维度就是类别数）
	ground_truth = np.zeros([1,n_classes], dtype=np.float32)#数据类型是float32型
	ground_truth[0][label_index] = 1.0#让这个类的索引对应位的值取1
	#bottleneck和groundtruth并入batch中
        if i==0:
            bottlenecks=bottleneck
            ground_truths=ground_truth
        else: 
            bottlenecks=np.concatenate((bottlenecks,bottleneck))
            ground_truths=np.concatenate((ground_truths,ground_truth))

        i+=1
        if i<how_many:
            continue
        else:
            break

    #愉快地返回
    return bottlenecks , ground_truths



		

def get_or_create_bottleneck(sess, video_lists, label_name, index, category, npy_data_tensor, bottleneck_tensor):
    flag=True

    #获取视频路径
    video_path = get_video_path(video_lists, INPUT_DATA, label_name, index, category)
    try:
	npy_data = np.load(video_path)
    except:
        print('video wrong')
        flag=False
        bottleneck_values=np.array([])
        return bottleneck_values,flag
    #取前64帧
    npy_data=npy_data[0:1,0:64,0:224,0:224,0:3]
    if npy_data.shape!=(1,64,224,224,3):
        flag=False
        bottleneck_values=np.array([])
        return bottleneck_values,flag

    #计算bottleneck!!!!!!!!!!！
    bottleneck_values = run_bottleneck_on_video(sess, npy_data, npy_data_tensor, bottleneck_tensor)
    bottleneck_values=bottleneck_values.reshape(1,8,7,7,1024)
    #print(bottleneck_values.shape)
    
    
    #返回bottleneck_value
    return bottleneck_values,flag


def get_bottleneck_path(video_lists, label_name, index, category):
    return get_video_path(video_lists, CACHE_DIR, label_name, index, category) + '.npy'


def get_video_path(video_lists, video_dir, label_name, index, category):
    label_lists = video_lists[label_name]
    category_list = label_lists[category]
    mod_index = index % len(category_list)
    base_name = category_list[mod_index]
    sub_dir = label_lists['dir']
    full_path = os.path.join(video_dir, sub_dir, base_name)
    return full_path

def run_bottleneck_on_video(sess, npy_data, npy_data_tensor,bottleneck_tensor):
    bottleneck_values = sess.run(bottleneck_tensor, {npy_data_tensor: npy_data})

    bottleneck_values = np.squeeze(bottleneck_values)
	
    return bottleneck_values
