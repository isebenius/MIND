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

This implementation is designed to automatcally compute MIND networks given the default outputs of FreeSurfer. MIND networks can thus be calculated easily as follows:

```
## Specify path to surfer directory. This is the path to the Freesurfer folder containing all standard output directories (e.g. surf, mri, label)
path_to_surf_dir = '/path/to/surfer/dir' 

## Specify features to include in MIND calculation. Any combination of the following five features are currently supported.
features = ['CT','MC','Vol','SD','SA'] 

## Select which parcellation to use. This has been tested on Desikan Killiany (DK), HCP-Glasser, DK-308 and DK-318 parcellations.
parcellation = 'aparc' 

## Returns a dataframe of regions X regions containing the final MIND network.
MIND = compute_MIND(path_to_surf_dir, features, parcellation) 

```

## Required files
Basic usage of MIND requires the vertex-level data stored in the surf/ folder (i.e. ?h.curv, ?h.thickness, etc.), in addition to the .annot files in the label/ folder which parcellate the vertex-level data.

Importantly, this code has only been tested using output from Freesurfer v5.3 and with the DK, DK-318, and HCP parcellations. Using different templates or versions of FreeSurfer will require you to adapt this code due to slightly different naming conventions. For example, the naming convention of 'unknown' brain regions, which are dropped, differs between parcellations. Thus, if you use MIND with other parcellations or versions of FreeSurfer, you'll have to make small manual changes to the code to comply with idiosyncratic naming conventions (e.g. altering line 57 of get_vertex_df.py to set the unknown_regions variable to include all unwanted regions).

## Including additional features
If you would like to include additional features from volumetric measurements from other modalities (e.g. FA or MD from DWI images), you can do this by registering the DTI image to T1 image used by FreeSurfer e.g. by using the B0 image and or mri_coreg or bbregister commands. Then, you can use the mri_vol2surf command to project the volumetric data to surface fiels. You will then need to adapt get_vertex_df.py to handle these new features and files. 

## Citing

If you use this software to compute MIND networks in your research, please cite the following paper:

Sebenius, Isaac et al. MIND Networks: Robust Estimation of Structural Similarity from Brain MRI. bioRxiv (2022). doi: https://doi.org/10.1101/2022.10.12.511922
