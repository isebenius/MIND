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
