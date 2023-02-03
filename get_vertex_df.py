import sys
import numpy as np
import os
import pandas as pd
from os.path import exists
from nibabel.freesurfer.io import read_morph_data, read_annot
from nibabel.freesurfer.mghformat import load
from collections import defaultdict
from MIND_helpers import calculate_mind_network, is_outlier

def get_vertex_df(surf_dir, features, parcellation):

    '''
    INPUT SPECIFICATIONS:
    • surf_dir (str) : This is a string the location containing all relevant directories output by FreeSurfer (i.e. label, mri, surf).

    • features (list):
        This function accepts the "features" argument as a list containing items in the following forms:
            str: 

                • One of ['CT','Vol','SA','MC','SD']. In this form, the function will automatically assume that the requested features are found in the surf_dir/surf directory and correspond to the following files:
                    CT: ?h.thickness
                    Vol: ?h.volume
                    SA: ?h.area
                    MC: ?h.curv
                    SD: ?h.sulc 

                • You may also pass a string in the form 'thickness', 'volume', 'sulc', etc, which refer directly to default files already found in the surf_dir/surf directory for both rh and lh.
                For example, the function will interpret the entry 'thickness' to refer to the files surf_dir/surf/lh.thickness and surf_dir/surf/rh.thickness

                • Finally, you may pass a string in the form of a FULL path as follows: with a question mark '?' indicating the position specifying the hemisphere such as "full/path/to/?h.feature".
                Using this formulation will cause the command to look for files that exactly match both "full/path/to/lh.feature" and "full/path/to/rh.feature". If the left and right version of the files aren't exactly the same otherwise, this won't work.


            tuple: (path/to/lh_surface_feature, path/to/rh_surface_feature)
                • If you would rather pass other features directly into the function, you must specify the locations (using paths) of both the left and right versions of each desired feature as a tuple.
                **The files must be readable by nibabel's read_morph_data function, i.e. in FreeSurfer's surface format!***
                So for example, if you have used the provided register_and_vol2surf function to generate surface maps of fractional anisotropy in a separate folder, you could pass them as an element in the list like:
                (path/to/lh.FA.mgh, path/to/rh.FA.mgh)

        A valid list of feature values combining these different input types would therefore be: ['CT','SD',(path/to/lh_feature1, path/to/rh_feature1), (path/to/lh_feature2, path/to/rh_feature2)] 
    
    • parcellation (str): This is a string the location containing parcellation scheme to be used. The files 'lh.' + parcellation + '.annot' and 'rh.' + parcellation + '.annot' must exist inside the surf_dir/label directory.
    '''

    #specify data locations
    surfer_location = surf_dir + '/'

    #Check inputs!
    if (exists(surfer_location + '/label/lh.' + parcellation + '.annot') == False) or (exists(surfer_location + '/label/rh.' + parcellation + '.annot') == False):
        raise Exception('Parcellation files not found.')

    all_shorthand_features = ['CT','Vol','SA','MC','SD']
    all_shorthand_features_dict = dict(zip(all_shorthand_features, ['thickness','volume','area','curv','sulc']))
    
    lh_feature_locs = []
    rh_feature_locs = []

    #Check feature inputs, store location of files
    for feature in features:
        if feature in all_shorthand_features:
            lh_loc = surfer_location + 'surf/lh.' + all_shorthand_features_dict[feature]
            rh_loc = surfer_location + 'surf/rh.' + all_shorthand_features_dict[feature]
            
            if (exists(lh_loc) == False) or (exists(rh_loc) == False):
                raise Exception('Feature for input "' + feature +'" not found.')
            else:
                lh_feature_locs.append(lh_loc)
                rh_feature_locs.append(rh_loc)

        elif type(feature) is str:

            if len(feature.split('/')) == 1:
                lh_loc = surfer_location + 'surf/lh.' + feature
                rh_loc = surfer_location + 'surf/rh.' + feature
                
                if (exists(lh_loc) == False) or (exists(rh_loc) == False):
                    raise Exception('Feature for input "' + feature +'" not found.')

                else:
                    lh_feature_locs.append(lh_loc)
                    rh_feature_locs.append(rh_loc)

            else:
                lh_loc = feature.split('/')
                lh_loc[-1] = 'l' + lh_loc[-1][1:]
                lh_loc = '/'.join(lh_loc)

                rh_loc = feature.split('/')
                rh_loc[-1] = 'r' + rh_loc[-1][1:]
                rh_loc = '/'.join(rh_loc)
                
                if (exists(lh_loc) == False) or (exists(rh_loc) == False):
                    raise Exception('Feature for input "' + feature +'" not found.')

                else:
                    lh_feature_locs.append(lh_loc)
                    rh_feature_locs.append(rh_loc)

        elif type(feature) is tuple:

            lh_loc = feature[0]
            rh_loc = feature[1]
            
            if (exists(lh_loc) == False) or (exists(rh_loc) == False):
                raise Exception('Feature for input "' + feature[0] +'" or "' + feature[1] +'" not found.')

            else:
                lh_feature_locs.append(lh_loc)
                rh_feature_locs.append(rh_loc)

        else:
            raise Exception('Unrecognized format for feature input: ', feature)

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
        print(hemi)
        hemi_data_dict = defaultdict()

        if hemi == 'lh':
            print('Loading left hemisphere data:')

            for i, lh_feature_loc in enumerate(lh_feature_locs):
                print(lh_feature_loc)
                #check for mgh/mgz format vs regular curv files
                if lh_feature_loc.endswith('mgh') or lh_feature_loc.endswith('mgz'):
                    hemi_data_dict['Feature_' + str(i)] = load(lh_feature_loc).get_fdata().flatten()
                else:
                    hemi_data_dict['Feature_' + str(i)] = read_morph_data(lh_feature_loc)

        elif hemi == 'rh':
            print('Loading right hemisphere data:')

            for i, rh_feature_loc in enumerate(rh_feature_locs):

                if rh_feature_loc.endswith('mgh') or rh_feature_loc.endswith('mgz'):
                    hemi_data_dict['Feature_' + str(i)] = load(rh_feature_loc).get_fdata().flatten()
                else:
                    hemi_data_dict['Feature_' + str(i)] = read_morph_data(rh_feature_loc)

        used_features = list(hemi_data_dict.keys())
        print(used_features)
        hemi_data = np.zeros((len(used_features) + 1, len(annot_dict[hemi][0])))

        hemi_data[0] = annot_dict[hemi][0]
        for i, feature in enumerate(used_features):
            print(i, feature)
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
    return vertex_data, combined_regions, used_features
