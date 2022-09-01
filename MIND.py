import sys
import os
import numpy as np
import pandas as pd
from MIND_helpers import calculate_mind_network, is_outlier
from get_vertex_df import get_vertex_df

def compute_MIND(surf_dir, features, parcellation):

	vertex_data, regions = get_vertex_df(surf_dir, features, parcellation)

	features_requested = features
	features_available = vertex_data.columns[1:]

	for feat in features_requested:
		if feat not in features_available:
			raise Exception(str(feat) + ' not available')

	features_used = [x for x in features_requested if x in features_available]

	'''
	Filter the data, do some QC checks here.

	-The important step is to remove vertices with 
	zero thickness, zero volume, or zero surface area, as these are degenerate and make no physical sense.

	I also do very lenient outlier removal using using MAD scores.
	MAD roughly assumes a normal distribution so I use a very large tolerace (7 adjusted z-score threshhold for now)
	in order to only get rid of really problematic outliers - the KL step shouldn't be too
	affected by smaller ones, and we don't want to be getting rid of signal or changing the distirbution in 
	specific regions. THis step could be removed altogether and it would be fine.

	Other things like log-transforms could all be done here, but should probably be applied with caution.
	(After all one of the big benefits of the KL method is it doesn't assume normality! 
	And by transforming the data it becomes arguably less interpretable/might be other issues there.)

	To double check everything, please look at histograms of individual features to make sure everything looks ok.

	'''

	columns = ['Label'] + features_used

	if 'CT' in vertex_data.columns:
		vertex_data = vertex_data.drop(vertex_data[vertex_data['CT'] == 0].index)

	if 'Vol' in vertex_data.columns:
		vertex_data = vertex_data.drop(vertex_data[vertex_data['Vol'] == 0].index)

	if 'SA' in vertex_data.columns:
		vertex_data = vertex_data.drop(vertex_data[vertex_data['SA'] == 0].index)

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
	#Save output
	#fname = 'MIND.' + parcellation + '.' + '_'.join(sorted(features_used)) + '.csv'
	#MIND.to_csv(outdir+'/'+fname)
	#np.savetxt(outdir + '/' + parcellation + "_regions.csv", combined_regions, delimiter = ',', fmt="%s")



