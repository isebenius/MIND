import os
from nipype.interfaces.freesurfer import BBRegister, SampleToSurface, ApplyVolTransform
from nipype.interfaces import afni
import nipype.interfaces.freesurfer as fs

#Must have SUBJECTS_DIR set as per standard Freesurfer conventions.

def register_and_vol2surf(mov, subject_id, out_dir, b0 = None, feature_name = 'vol-feature', contrast = 't2', sampling_units = 'frac', sampling_range = (0.2,0.8,0.1), sampling_method = 'average', cleanup=True):
	
	'''
	This commands registers a volumetric image to T1 then projects to the white surface.
	Note that the SUBJECTS_DIR environmental variable needs to be set correctly, and Freesurfer available on the system. 
	
	Description of inputs:

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

	out_reg_file = out_dir + '/' + feature_name + '-T1-reg.dat'

	if b0 == None:
		b0 == mov

	bbreg = BBRegister(subject_id=subject_id, source_file=b0, subjects_dir=os.environ.get("SUBJECTS_DIR"), init='fsl', contrast_type=contrast, out_reg_file = out_reg_file)
	os.system(bbreg.cmdline)
	#bbregister
	#resample to surface, save to the surf folder

	for hemi in ['lh','rh']:

		sampler = SampleToSurface(subject_id=subject_id, hemi=hemi, cortex_mask = True, \
			subjects_dir=os.environ.get("SUBJECTS_DIR"), source_file = mov, reg_file=out_reg_file, \
			sampling_method = sampling_method, sampling_units = sampling_units, sampling_range = sampling_range, \
			out_file = out_dir + '/' + hemi + '.' + feature_name + '.mgz', out_type = 'mgz')
		sampler.run() 

	#Remove the generated registration file because nobody wants that lying around!
	if cleanup==True:
		os.system('rm ' + out_reg_file + '*')

def calculate_surface_t1t2_ratio(t2_loc, subject_id, out_dir, t1_loc = None, feature_name = 'T2', contrast = 't2', sampling_units = 'frac', sampling_range = (0.2,0.8,0.1), sampling_method = 'average', cleanup=True):

	'''
	This commands registers T2 to T1, divides T1 by the registered T2, then projects to the white surface.
	Note that the SUBJECTS_DIR environmental variable needs to be set correctly, and Freesurfer available on the system. 
	We recommend using the T2.mgz file in the mri/ folder output from freesurfer.

	Description of inputs:

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

	out_reg_file = out_dir + '/' + feature_name + '-T1-reg.dat'
	bbreg = BBRegister(subject_id=subject_id, source_file=t2_loc, init='fsl', subjects_dir=os.environ.get("SUBJECTS_DIR"), contrast_type=contrast, out_reg_file = out_reg_file)
	os.system(bbreg.cmdline)
	#bbregister
	#apply volumetric transform to the T1 and T2 images.

	applyreg = fs.ApplyVolTransform()
	applyreg.inputs.source_file = t2_loc
	applyreg.inputs.reg_file = out_reg_file
	applyreg.inputs.transformed_file = out_dir + '/T2-warped-to-T1.nii'
	applyreg.inputs.fs_target = True
	os.system(applyreg.cmdline)

	if t1_loc == None:
		t1_loc = os.environ.get('SUBJECTS_DIR') + '/' + subject_id + '/mri/T1.mgz'

	mc = fs.MRIConvert()
	mc.inputs.in_file = t1_loc
	mc.inputs.out_file = out_dir + '/T1.nii.gz'
	mc.inputs.out_type = 'niigz'
	os.system(mc.cmdline)

	calc = afni.Calc()
	calc.inputs.in_file_a = out_dir + '/T1.nii.gz'
	calc.inputs.in_file_b = out_dir + '/T2-warped-to-T1.nii'
	calc.inputs.expr='a/b'
	calc.inputs.out_file = out_dir + '/T1-over-T2.nii.gz'
	calc.inputs.outputtype = 'NIFTI_GZ'
	os.system(calc.cmdline + ' -float -fscale')

	for hemi in ['lh','rh']:

		sampler = SampleToSurface(subject_id=subject_id, hemi=hemi, subjects_dir=os.environ.get("SUBJECTS_DIR"), \
			source_file = out_dir + '/T1-over-T2.nii.gz', cortex_mask = True, reg_file=out_reg_file, 
			sampling_method = sampling_method, sampling_units = sampling_units, \
			sampling_range = sampling_range, out_file = out_dir + '/' + hemi + '.T1-over-T2.mgz', out_type = 'mgz')
		res = sampler.run() 

	#Cleanup if desired
	if cleanup==True:
		os.system('rm ' + out_reg_file + '*')
		os.system('rm ' + out_dir + '/T2-warped-to-T1.nii')
		os.system('rm ' + out_dir + '/T1-over-T2.nii.gz')
		#get rid of the converted temporary T1 file
		os.system('rm ' + out_dir + '/T1.nii.gz')
