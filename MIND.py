import sys
import os
import numpy as np
import pandas as pd
from MIND_helpers import calculate_mind_network, is_outlier
from get_vertex_df import get_vertex_df

def compute_MIND(surf_dir, features, parcellation, filter_vertices=False):

	vertex_data, regions, features_used = get_vertex_df(surf_dir, features, parcellation)
	
	'''
	Filter the data, do some QC checks here.
	To double check everything, please look at histograms of individual features to make sure everything looks ok.

	'''

	columns = ['Label'] + features_used
	
	feature_conv_dict = dict(zip(list(features), list(features_used)))
	#The filter_vertices parameter determines you want to filter out all the non-biologically feasible vertices (i.e. any of volume, surface area or cortical thickness equalling zero)	
	if filter_vertices == True:

		if 'CT' in features:
			vertex_data = vertex_data.drop(vertex_data[vertex_data[feature_conv_dict['CT']] == 0].index)

		if 'Vol' in features:
			vertex_data = vertex_data.drop(vertex_data[vertex_data[feature_conv_dict['Vol']] == 0].index)

		if 'SA' in features:
			vertex_data = vertex_data.drop(vertex_data[vertex_data[feature_conv_dict['SA']] == 0].index)
	
	vertex_data = vertex_data[columns]

	#standardize across the brain for each feature to get each dimension to roughly the same scale.
	for x in features_used:
		vertex_data[x] = (vertex_data[x] - vertex_data[x].mean())/vertex_data[x].std()

	#Drop outliers. This drops vertices with an MAD score in ANY of the used features. Can be customized.
	# z_score_threshhold = 7
	# outliers_per_features = np.array([is_outlier(vertex_data[x].values, z_score_threshhold) for x in features_used]).T
	# vertex_data = vertex_data.loc[np.sum(outliers_per_features, axis = 1) == 0]

	print('Computing MIND...')
	#calculate MIND network
	MIND = calculate_mind_network(vertex_data, features_used, regions)

	print('Done!')
	return MIND



