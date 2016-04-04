import numpy as np
import random
import os
from glob import glob
from skimage import io
from sklearn.feature_extraction.image import extract_patches_2d

np.random.seed(5)
train_files = glob('Patches_Train/**')

def find_patches(training_images, class_num, num_samples, patch_size=(65,65)):
    '''
    Method for sampling slices with evenly distributed classes
    INPUT:  (1) list 'training_images': all training images to select from
            (2) int 'class_num': class to sample from choice of {0, 1, 2, 3, 4}.
            (3) tuple 'patch_size': dimensions of patches to be generated defaults to 65 x 65
    OUTPUT: (1) num_samples patches from class 'class_num' randomly selected. note- if class_num is 0, will choose patches randomly, not exclusively 0s.
    '''
    ct = 0 # keep track of patch number
    h,w = patch_size[0], patch_size[1]
    patches = [] #list of all patches (X)
    labels = np.full(num_samples, class_num) # y
    if class_num == 0:
        print 'Finding patches of class 0...'
        while ct < num_samples:
            im_path = random.choice(training_images)
            patch, label = random_patches(im_path, patch_size = patch_size)
            patches.append(patch)
            labels[ct] = label # acutal label of patch
            # l.append(label)
            # labels.append(label[(h+1)/2][(w+1)/2])
            ct += 1
        print 'Done'
        return np.array(patches), labels

    print 'Finding patches of class {}...'.format(class_num)
    while ct < num_samples:
        im_path = random.choice(training_images) # select image to sample from
        fn = os.path.basename(im_path)
        label = io.imread('Labels/' + fn[:-4] + 'L.png')
        if class_num not in np.unique(label): # no pixel label class_num in img
            continue
        img = io.imread(im_path).reshape(5, 240, 240)[:-1] # exclude label slice
        p = random.choice(np.argwhere(label == class_num)) # center pixel
        while p[0] < h/2 or p[1] < h/2: # if patch won't fit
            continue
        p_ix = (p[0]-(h/2), p[0]+((h+1)/2), p[1]-(w/2), p[1]+((w+1)/2)) # patch index
        patch = np.array([i[p_ix[0]:p_ix[1], p_ix[2]:p_ix[3]] for i in img])
        # l.append(label[p_ix[0]:p_ix[1], p_ix[2]:p_ix[3]])
        patches.append(patch) # patch = (n_chan, h, w)
        ct += 1
    print 'Done'
    return np.array(patches), labels

def random_patches(im_path, patch_size = (65,65)):
    '''
    method for randomly sampling patches from a slice
    INPUT:  (1) string 'im_path': path to image to sample from
            (2) tuple 'patch_size': size (in pixels) of patches.
    '''
    fn = os.path.basename(im_path)
    patch_lst = []
    label = io.imread('Labels/' + fn[:-4] + 'L.png')
    imgs = (io.imread(im_path).reshape(5, 240, 240)) # exclude label
    imgs[4] = label
    for img in imgs:
        patch_lst.append(extract_patches_2d(img, patch_size, max_patches = 1, random_state=5)[0]) #set rs for same patch ix among modes
    patch = np.array(patch_lst[:-1])
    patch_label = np.array(patch_lst[-1][(patch_size[0] + 1) / 2][(patch_size[1] + 1) / 2]) # center pixel of patch
    return np.array(patch), patch_label

def make_training_patches(training_images, num_total, balanced_classes = True, patch_size = (65,65)):
    '''
    Outputs an X and y to train cnn on
    INPUT   (1) list 'training_images': list of all training images to draw from randomly
            (2) int 'num_total': total number pf patches to produce
            (3) bool 'balanced_classes': True for balanced classes. If false, will randomly sample patches leading to high amnt of background
            (4) tuple 'patch_size': size(in pixels) of patches to select
    OUTPUT  (1) array 'patches': randomly selected patches. shape:
                (num_total, n_chan (4), patch height, patch width)
    '''
    if balanced_classes:
        per_class = num_total / 5
        patches, labels = [], [] # list of tuples (patche, label)
        for i in xrange(5):
            p, l = find_patches(training_images, i, per_class)
            patches.append(p)
            labels.append(l)
        return np.array(patches).reshape(num_total, 4, patch_size[0], patch_size[1]), np.array(labels).reshape(num_total)
    else:
        patches, labels = find_patches(training_images, 0, num_total)
        return np.array(patches), np.array(labels)

if __name__ == '__main__':
    train_imgs = glob('Patches_Train/*.png')
    X, y = make_training_patches(train_imgs, 320)


## GRAVEYARD ##

# def generate_patches(img_path, patch_size=(65,65), num_patches = 10):
#     '''
#     Generates patches (num_chan, patch_h, patch_w) for an input image
#     INPUT:  (1) string 'img_path': path to imput image (png, strip of slices)
#             (2) tuple 'patch_size': dimensions of patches to be used in net
#             (3) int 'num_patches': number of patches to be generated per slice.
#     OUTPUT: (1) list of scan patches: (num_slices * num_patches, num_channels, patch_h, patch_w)
#             (2) list of label patches: (num_slices * num_patches, patch_h, patch_w)
#     '''
#     patch_lst = [] # list of lists: patches for each slice (same idxs)
#     patch_labels = []
#     fn = os.path.basename(im_path)
#     label = io.imread('Labels/' + fn[:-4] + 'L.png')
#     slices = io.imread(img_path).reshape(5,240,240)[:-1] # (chan + gt, h, w)
#     slices = slices.append(label)
#     for img in slices:
#         patch_lst.append(extract_patches_2d(img, patch_size, max_patches = num_patches, random_state=5)) #set rs for same patch ix among modes
#     patches = np.array(zip(patch_lst[0], patch_lst[1], patch_lst[2], patch_lst[3]))
#     patch_labels = np.array([i[patch_size[0] / 2][patch_size[1]/2] for i in patch_lst[-1]])
#     return patches, patch_labels

    # for slice_strip in self.normed_slices: # slice = strip of 5 images
    #     slices = slice_strip.reshape(5,240,240)
        # for img in slices:
        #     # get list of patches corresponding to each image in slices
        #     patch_list.append(extract_patches_2d(img, patch_size, max_patches = num_patches, random_state=5)) #set rs for same patch ix among modes
        # self.patches.append(zip(patch_list[0], patch_list[1], patch_list[2], patch_list[3]))
        # self.patch_labels.append(patch_list[-1])
