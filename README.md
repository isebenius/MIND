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
By default, the _features_ parameter accepts some combination of the elements ['CT','MC','Vol','SD','SA'] as the features to include, based on the ?h.thickness, ?h.curv, ?h.volume, ?h.sulc, and ?h.area Freesurfer surface features. 

However, additional features can be included to MIND computation by including the full path to the other files, provided they are in FreeSurfer's surface overlay format and follow the naming convention "?h.feature." For example, if you wanted to construct a MIND network using cortical thickness as well as a distinct feature A, you could pass the following combination of parameters as the 'features' variable in _compute_MIND_:

```
features = ['CT', 'path/to/?h.feature']
```
A more complete specificatin of the accepted input formats for the _features_ parameter is found in the function specification in _get_vertex_df.py_. 

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

Sebenius, Isaac et al. MIND Networks: Robust Estimation of Structural Similarity from Brain MRI. bioRxiv (2022). doi: https://doi.org/10.1101/2022.10.12.511922
