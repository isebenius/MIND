# MIND
This repository contains a Python implementation of Morphometric INverse Divergence (MIND) calculation for the estimation of structural similarity networks in the brain.

This implementation is designed to automatcally compute MIND networks given the default outputs of FreeSurfer. MIND networks can be calculated easily as follows:

```
path_to_surf_dir = '/path/to/surfer/dir' #this is the path to the Freesurfer folder containing all standard output directories (e.g. surf, mri, label)
features = ['CT','MC','Vol','SD','SA'] #Any combination of these five features are currently supported.
parcellation = 'aparc' #This has been tested on Desikan Killiany (DK), HCP-Glasser, DK-308 and DK-318 parcellations.
MIND = compute_MIND(path_to_surf_dir, features, parcellation) #Returns a dataframe of regions X regions containing the final MIND network

```
