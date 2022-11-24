import sys
import numpy as np
import os
import pandas as pd
from os.path import exists
from surfer import project_volume_data
from nibabel.freesurfer.io import read_morph_data, read_annot
from collections import defaultdict
from MIND_helpers import calculate_mind_network, is_outlier

def get_vertex_df(surf_dir, features, parcellation):

    #specify data locations
    surfer_location = surf_dir + '/'

    #All possible features you could want.
    all_features = ['CT','Vol','SA','MC','SD','T1T2']

    for feature in features:
        if feature not in all_features:
            raise Exception(str(feature) + ' is invalid or not yet available. Avalailable features are: SA, Vol, CT, MC, SD, T1T2.')
    
    n_features = len(all_features)

    #Get annotation files
    lh_annot = read_annot(surfer_location + '/label/lh.' + parcellation + '.annot', orig_ids = True)
    rh_annot = read_annot(surfer_location + '/label/rh.' + parcellation + '.annot', orig_ids = True)

    annot_dict = {'lh':lh_annot, 'rh':rh_annot}

    '''
    The regions in the lh and rh need to be renamed and distinct. 

    So, here we append lh_ or rh_ to the front of each region name and make a conversion dict.
    This will likely need to change for different processing pipelines (FS versions) and datasets etc.
    so make sure this dict is correct and looks good.
    '''

    lh_region_names = ['lh_' + str(x).split("'")[1] for x in lh_annot[2]]
    rh_region_names = ['rh_' + str(x).split("'")[1] for x in rh_annot[2]]

    lh_convert_dict = dict(zip(lh_annot[1][:,-1], lh_region_names))
    rh_convert_dict = dict(zip(rh_annot[1][:,-1], rh_region_names))

    convert_dicts = {'lh': lh_convert_dict,\
                    'rh': rh_convert_dict}

    used_labels_l = np.intersect1d(np.unique(lh_annot[0]), list(lh_convert_dict.keys()))
    used_labels_r = np.intersect1d(np.unique(rh_annot[0]), list(rh_convert_dict.keys()))

    used_labels = {'lh': used_labels_l,\
                    'rh': used_labels_r}


    used_regions_l = np.array([value for key, value in lh_convert_dict.items() if key in used_labels_l])
    used_regions_r = np.array([value for key, value in rh_convert_dict.items() if key in used_labels_r])

    combined_regions = np.hstack((used_regions_l, used_regions_r))
    unknown_regions = [x for x in combined_regions if (('?' in x) | ('unknown' in x) | ('Unknown' in x) | ('Medial_Wall' in x) | (len(x) == 3))]
    combined_regions = np.array([x for x in combined_regions if x not in unknown_regions])

    vertex_data_dict = defaultdict()

    #Now load up all the vertex-level data!
    for hemi in ['lh','rh']:
        
        if hemi == 'lh':
            print('Loading left hemisphere data:')

        elif hemi == 'rh':
            print('Loading right hemisphere data:')

        hemi_data_dict = defaultdict()

        ct_loc = surfer_location + 'surf/' + hemi + '.thickness'
        vol_loc = surfer_location + 'surf/' + hemi + '.volume'
        sa_loc = surfer_location + 'surf/' + hemi + '.area'
        mc_loc = surfer_location + 'surf/' + hemi + '.curv'
        sd_loc = surfer_location + 'surf/' + hemi + '.sulc'
        
        T1_loc = surfer_location + 'mri/T1.mgz'
        T2_loc = surfer_location + 'mri/T2.mgz'

        if exists(ct_loc):
            print("CT file exists")
            hemi_data_dict['CT'] = read_morph_data(ct_loc)
            
        if exists(vol_loc):
            print("Vol file exists")
            hemi_data_dict['Vol'] = read_morph_data(vol_loc)
        
        if exists(mc_loc):
            print("MC file exists")
            hemi_data_dict['MC'] = read_morph_data(mc_loc)
            
        if exists(sa_loc):
            print("SA file exists")
            hemi_data_dict['SA'] = read_morph_data(sa_loc)
        
        if exists(sd_loc):
            print("SD file exists\n")
            hemi_data_dict['SD'] = read_morph_data(sd_loc)
        
        if exists(T1_loc) & exists(T2_loc):
            print('T1/T2 files exist')
            temp = surf_dir.split('/')
            temp = [x for x in temp if ((len(x)!= 0) or x == '/')]
            subject = temp[-1]
            subjects_dir = '_'.join(temp[0:-1])
            os.system('export SUBJECTS_DIR='+subjects_dir)
            T1=project_volume_data(filepath = T1_loc, hemi = hemi, subject_id = subject, projsum = 'point', projarg=0.5)
            T2=project_volume_data(filepath = T2_loc, hemi = hemi, subject_id = subject, projsum = 'point', projarg=0.5)
            hemi_data_dict['T1T2'] = T1/T2

        used_features = [x for x in all_features if x in list(hemi_data_dict.keys())]
        
        hemi_data = np.zeros((len(used_features) + 1, len(annot_dict[hemi][0])))

        hemi_data[0] = annot_dict[hemi][0]
        for i, feature in enumerate(used_features):
            hemi_data[i + 1] = hemi_data_dict[feature]
        
        col_names = ['Label'] + used_features
        hemi_data = pd.DataFrame(hemi_data.T, columns = col_names)
        
        #Select only the vertices that map to regions.
        hemi_data = hemi_data.loc[hemi_data['Label'].isin(used_labels[hemi])]
        
        hemi_data["Label"] = hemi_data["Label"].map(convert_dicts[hemi])
        vertex_data_dict[hemi] = hemi_data

    vertex_data = pd.concat([vertex_data_dict['lh'], vertex_data_dict['rh']], ignore_index = True)

    #Output data
    print("features used: ")
    print(used_features)
    return vertex_data, combined_regions
