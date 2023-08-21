# MIND
This repository contains a Python implementation of Morphometric INverse Divergence (MIND) calculation for the estimation of structural similarity networks in the brain.

## Installation
You can download this code by cloning it as follows: 
```
git clone https://github.com/isebenius/MIND.git 
```
## MIND computation
The main function for calculation MIND networks is the compute_mind() function within MIND.py. This can be imported into a script as follows:
```
import sys
sys.path.insert(1, '/path/to/MIND/code/')
from MIND import compute_MIND
```

This implementation is designed to automatcally compute MIND networks given the default outputs of FreeSurfer. In its most simlple instance, MIND networks can be calculated as follows:

```
## Specify path to surfer directory. This is the path to the Freesurfer folder containing all standard output directories (e.g. surf, mri, label)
path_to_surf_dir = '/path/to/surfer/dir' 

## Specify features to include in MIND calculation. The following abbreviations specifies the ?h.thickness, ?h.curv, ?h.volume, ?h.sulc, and ?h.area Freesurfer surface features.
features = ['CT','MC','Vol','SD','SA'] 

## Select which parcellation to use. This has been tested on Desikan Killiany (DK), HCP-Glasser, DK-308 and DK-318 parcellations.
parcellation = 'aparc' 

## Returns a dataframe of regions X regions containing the final MIND network.
MIND = compute_MIND(path_to_surf_dir, features, parcellation) 

```
## Required files
Basic usage of MIND requires vertex-level data in FreeSrufer surface overlay format (by default stored in the surf/ folder, i.e. ?h.curv, ?h.thickness, etc., but also can be in a specified alternate location), in addition to the .annot files in the label/ folder which parcellate the vertex-level data.

Importantly, this code has only been tested using output from Freesurfer v5.3 and with the DK, DK-318, and HCP parcellations. Using different templates or versions of FreeSurfer will require you to adapt this code due to slightly different naming conventions. For example, the naming convention of 'unknown' brain regions, which are dropped, differs between parcellations. Thus, if you use MIND with other parcellations or versions of FreeSurfer, you'll have to make small manual changes to the code to comply with idiosyncratic naming conventions (e.g. altering line 149 of get_vertex_df.py to set the unknown_regions variable to include all unwanted regions).

## Passing additional features to the compute_MIND command:
By default, the _features_ parameter accepts some combination of the elements [CT,MC,Vol,SD,SA] as the features to include, based on the ?h.thickness, ?h.curv, ?h.volume, ?h.sulc, and ?h.area Freesurfer surface features. 

Additional features can be included to MIND computation by including the full path to the other files, provided they are in FreeSurfer's surface overlay format and follow the naming convention "?h.feature." For example, if you wanted to construct a MIND network using cortical thickness as well as a distinct feature A, you could pass the following combination of parameters as the 'features' variable in _compute_MIND_:

```
features = ['CT', 'path/to/?h.feature']
```
A more complete specification of the accepted input formats for the _compute_MIND_ command is as follows, reiterated in the function description of _get_vertex_df.py_.

```
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
```
## Including volumetric features
We include additional functions to generate surface maps features from volumetric MRI features using _nipype_, both in _register_and_vol2surf.py_. The first function, _register_and_vol2surf_, registers a volumetric image to T1 then projects to the white surface. The second related function, _calculate_surface_t1t2_ratio_, registers T2 to T1, divides T1 by the registered T2, then projects to the white surface. As mentioned, features must be in vertex-space for inclusion into MIND network construction.

Usage of these functions requires both Freesurfer and afni to be installed and available on the system, and requires the specified subject to have been processed using FreeSurfer's _recon-all_ command.

```
function register_and_vol2surf(mov, subject_id, out_dir, b0 = None, feature_name = 'vol-feature', contrast = 't2', sampling_units = 'frac', sampling_range = (0.2,0.8,0.1), sampling_method = 'average', cleanup=True):
  '''
  This commands registers a volumetric image to T1 then projects to the white surface.
  
  	mov: the volume to be registered.
	subject_id: The subject id, found in SUBJECTS_DIR.
	out_dir: path to output files.
	b0: if registering DWI images, this is the image to use for registration (using the B0 or S0 is recommended).
	feature_name: the name of the feature you would like to project (e.g., FA etc.). This is just so the output files are named nicely.
	contrast: either 't1' or 't2' based on the contrast of the registration image:
	sampling units: either 'frac' or 'mm'
	sampling method: 'point’ or ‘max’ or ‘average,’ tells the command how to sample.
	sampling range: a float or a tuple of the form: (a float, a float, a float)) – Sampling range - a point or a tuple of (min, max, step).
	cleanup: boolean, whether to delete all intermediate files or not.
  '''
 
function calculate_surface_t1t2_ratio(t2_loc, subject_id, out_dir, t1_loc = None, feature_name = 'T2', contrast = 't2', sampling_units = 'frac', sampling_range = (0.2,0.8,0.1), sampling_method = 'average', cleanup=True):

  '''
  This commands registers T2 to T1, divides T1 by the registered T2, then projects to the white surface.
  We recommend using the T2.mgz file in the mri/ folder output from freesurfer.
  
  	mov: the volume to be registered.
	subject_id: The subject id, found in SUBJECTS_DIR.
	out_dir: path to output files.
	t1_loc: the location.
	feature_name: the name of the feature you would like to project (e.g., FA etc.). This is just so the output files are named nicely.
	contrast: either 't1' or 't2' based on the contrast of the registration image:
	sampling units: either 'frac' or 'mm'
	sampling method: 'point’ or ‘max’ or ‘average,’ tells the command how to sample.
	sampling range: a float or a tuple of the form: (a float, a float, a float)) – Sampling range - a point or a tuple of (min, max, step).
	cleanup: boolean, whether to delete all intermediate files or not.
   '''
   
```

After these commands have been run, the output surface files can then be passed as features into the _compute_MIND_ command.

## Citing

If you use this software to compute MIND networks in your research, please cite the following paper:

Sebenius, I., Seidlitz, J., Warrier, V. et al. Robust Estimation of Cortical Similarity Networks from Brain MRI. Nat Neurosci 26, 1461–1471 (2023). https://doi.org/10.1038/s41593-023-01376-7
