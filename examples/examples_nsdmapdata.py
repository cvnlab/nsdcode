"""
examples to use nsdcode
"""
import os
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from nsdcode.nsd_mapdata import NSDmapdata
from nsdcode.nsd_datalocation import nsd_datalocation
from nsdcode.nsd_output import nsd_write_fs
from nsdcode.utils import makeimagestack


# Map T1 anatomical to EPI space

# Here we map the 0.8-mm T1 to the 1-mm EPI space using cubic interpolation.
# The resulting T1 volume might be useful for viewing volume-based
# fMRI results against the anatomy.
subjix = 1
base_path = os.path.join('/path', 'to', 'NSD')

# initiate NSDmapdata
nsd = NSDmapdata(base_path)

nsd_dir = nsd_datalocation(base_path=base_path)
nsd_betas = nsd_datalocation(base_path=base_path, dir0='betas')

sourcedata = f'{nsd_dir}/ppdata/subj{subjix:02d}/anat/T1_0pt8_masked.nii.gz'
sourcespace = 'anat0pt8'
targetspace = 'func1pt0'
interpmethod = 'cubic'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# show the resulting transform
plt.imshow(makeimagestack(targetdata))
plt.show()

"""
# test case for comparing the matlab output
import seaborn as sns
import pandas as pd
compare matlab and python
# testA.nii.gz was generated with the code above in example_nsdmapdata.m
matlab_img = nib.load(
    'testA.nii.gz').get_data()
python_img = nib.load(
    f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz').get_data()
d = {'matlab': matlab_img.ravel(),
     'python':python_img.ravel()}
df = pd.DataFrame(data=d)
ax = sns.scatterplot(x="matlab", y="python", data=df)
"""
# let's test going from func1pt8mm to anat0pt8, but for a 4d-nifti
sourcedata = \
    f'{nsd_betas}/ppdata/subj{subjix:02d}/func1pt8mm/' + \
    'betas_fithrf_GLMdenoise_RR/betas_session01.nii.gz'
sourcespace = 'func1pt8'
targetspace = 'anat0pt8'
interpmethod = 'cubic'
nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype='cubic',
    badval=0,
    outputfile='test4D.nii.gz')

# To confirm correctness, compare the following:
#   test-anat1pt8-func1pt8-cubic.nii.gz
#   ppdata/subj01/func1pt8mm/mean.nii.gz


interpmethod = 'nearest'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# show the resulting transform
plt.imshow(makeimagestack(targetdata))

interpmethod = 'linear'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# show the resulting transform
plt.imshow(makeimagestack(targetdata))

# test going from func1pt8 to anat0pt8
sourcespace = 'func1pt8'
sourcedata = \
    f'{nsd_betas}/ppdata/subj{subjix:02d}/{sourcespace}mm/' + \
    'betas_fithrf_GLMdenoise_RR/meanbeta_session01.nii.gz'

targetspace = 'anat0pt8'
interpmethod = 'cubic'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# show the resulting transform
plt.imshow(makeimagestack(targetdata.astype(np.float32)/300), vmin=-5, vmax=5., cmap='RdBu_r')

interpmethod = 'nearest'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# show the resulting transform
plt.imshow(makeimagestack(targetdata.astype(np.float32)/300), vmin=-5, vmax=5., cmap='RdBu_r')

interpmethod = 'linear'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# show the resulting transform
plt.imshow(makeimagestack(targetdata.astype(np.float32)/300), vmin=-5, vmax=5., cmap='RdBu_r')

# test anat going from func1pt8 to anat0pt8
sourcespace = 'func1pt8'
sourcedata = f'{nsd_dir}/ppdata/subj{subjix:02d}/{sourcespace}mm/mean.nii.gz'
targetspace = 'anat0pt8'
interpmethod = 'cubic'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# show the resulting transform
plt.imshow(makeimagestack(targetdata), cmap='RdBu_r')


## Map EPI results to MNI space
# Here we take the variance explained (R2) value obtained for the "betas_fithrf_GLMdenoise_RR"
# GLM model in the first NSD session in the high-resolution 1-mm functional preparation,
# and map this to MNI space (which has 1-mm resolution).

sourcespace = 'func1pt0'
sourcedata = f'{nsd_betas}/ppdata/subj{subjix:02d}/func1mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz' 
targetspace = 'MNI'
targetdata = nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype='cubic',
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

plt.imshow(makeimagestack(targetdata))

# For comparison, we repeat the same operation but for the low-resolution
# 1.8-mm functional preparation.
sourcedata = f'{nsd_betas}/ppdata/subj{subjix:02d}/func1pt8mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz' 
sourcespace = 'func1pt8'
targetspace = 'MNI'
interpmethod = 'cubic'
nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile=f'test-{sourcespace}-{targetspace}-{interpmethod}.nii.gz')

# To assess the results, compare the following:
#   templates/MNI152_T1_1mm.nii.gz
#   testB_1mm.nii.gz
#   testB_1pt8mm.nii.gz
# Notice that the high- vs. low-resolution functional preparation makes a difference.

# To confirm sanity of the transformations, we can repeat the transformations for the
# mean EPI volume in the two different functional preparations.
sourcedata = f'{nsd_dir}/ppdata/subj{subjix:02d}/func1mm/mean_session01.nii.gz'
sourcespace = 'func1pt0'
targetspace = 'MNI'
interpmethod = 'cubic'
nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype=interpmethod,
    badval=0,
    outputfile='testC_1mm.nii.gz')


sourcedata = f'{nsd_dir}/ppdata/subj{subjix:02d}/func1pt8mm/mean_session01.nii.gz'  
nsd.fit(
    subjix,
    'func1pt8',
    'MNI',
    sourcedata,
    'cubic',
    badval=0,
    outputfile='testC_1pt8mm.nii.gz')

# Compare the above results to:
#   testC_1mm.nii.gz
#   testC_1pt8mm.nii.gz
# Notice that the two mean EPI volumes are spatially consistent but differ in
# the level of spatial detail.

## Map EPI results to surface space

# Here we take the same variance explained (R2) value described above
# and map it to the mid-gray native subject surface in the left hemisphere.
# This mapping is accomplished using a cubic interpolation of the data
# at each surface vertex location.

fsdir = os.path.join(nsd_datalocation(base_path=base_path), 'freesurfer', f'subj{subjix:02d}')
sourcedata = f'{nsd_betas}/ppdata/subj{subjix:02d}/func1mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz'  
nsd.fit(
    subjix,
    'func1pt0',
    'lh.layerB2',
    sourcedata,
    'cubic',
    badval=0,
    outputfile='lh.testD_layerB2.mgz',
    outputclass=None,
    fsdir=fsdir)


# let's repeat the above test, going from 1.8pt to to the vertices
sourcedata = f'{nsd_betas}/ppdata/subj{subjix:02d}/func1pt8mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz'  
sourcespace = 'func1pt8'
targetspace = 'lh.layerB1'
interpmethod = 'cubic'
nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype='cubic',
    badval=0,
    outputfile='lh.testD_layerB1.mgz',
    outputclass=None,
    fsdir=fsdir)


# Let's repeat the same operation but sample the data onto the other two surfaces.
# "layerB1", "layerB2", and "layerB3" correspond to 25%, 50%, and 75%
# of the distance from the pial to the white-matter surfaces, respectively.

nsd.fit(
    subjix,
    'func1pt0',
    'lh.layerB1',
    sourcedata,
    'cubic',
    badval=0,
    outputfile='lh.testD_layerB1.mgz',
    outputclass=None,
    fsdir=fsdir)

nsd.fit(
    subjix,
    'func1pt0',
    'lh.layerB3',
    sourcedata,
    'cubic',
    badval=0,
    outputfile='lh.testD_layerB3.mgz',
    outputclass=None,
    fsdir=fsdir)

# To assess the results, compare the following on the lh.inflated surface:
#   lh.testD_layerB1.mgz
#   lh.testD_layerB2.mgz
#   lh.testD_layerB3.mgz
# Notice that the results depend substantially on the surface onto which
# the data are sampled.

# We can map multiple datasets in one call to nsd.fit.m. In the following
# example, the file "R2run_session01.nii.gz" contains 12 different R2 values,
# one for each of the 12 runs conducted in the first NSD session. Each volume
# is independently mapped onto the lh.layerB2 surface, and the multiple
# surface-based outputs are saved into a single .mgz file.

sourcedata = f'{nsd_betas}/ppdata/subj{subjix:02d}/' + \
    'func1mm/betas_fithrf_GLMdenoise_RR/R2run_session01.nii.gz'
nsd.fit(
    subjix,
    'func1pt0',
    'lh.layerB2',
    sourcedata,
    'cubic',
    badval=0,
    outputfile='lh.testE.mgz',
    outputclass=None,
    fsdir=fsdir)

# We can also perform the mapping and omit having to write out a file to disk.
# Instead, we obtain the results in our workspace.
data = nsd.fit(
    subjix,
    'func1pt0',
    'lh.layerB2',
    sourcedata,
    'cubic',
    badval=0)

plt.plot(np.median(data, axis=0))
plt.xlabel('Run number')
plt.ylabel('Median R2')
##

# Map native subject surface results to fsaverage

# Here we repeat the mapping for variance explained (R2) for
# the three cortical depths, # accruing results in the workspace.
subjix = 1
sourcedata = \
    f'{nsd_betas}/ppdata/subj{subjix:02d}/func1mm/' + \
    'betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz'

data = []
for p in range(3):
    data.append(
        nsd.fit(
            subjix,
            'func1pt0',
            f'lh.layerB{p+1}',
            sourcedata,
            'cubic',
            badval=0
        )
    )

data = np.vstack(np.asarray(data))

# Now we average results across the three cortical depths and use
# nearest-neighbor interpolation to bring the result to fsaverage.
fsdir = os.path.join(nsd_datalocation(base_path=base_path), 'freesurfer', 'fsaverage')
nsd.fit(
    subjix,
    'lh.white',
    'fsaverage',
    np.mean(data, axis=0),
    interptype=None,
    badval=0,
    outputfile='lh.testF.mgz',
    fsdir=fsdir)

# Assess the results by inspecting on fsaverage's lh.inflated surface:
#   lh.testF.mgz
# and comparing this to the native subject's lh.inflated surface:
#   lh.testD_layerB2.mgz


# Inspect alignment of subjects to fsaverage
# Here we load each subject's native curvature and map it to fsaverage.
data = []
for subjix in range(1,9):
    a1 = nib.load(
        f'{nsd_dir}/freesurfer/subj{subjix:02d}/surf/lh.curvature.mgz').get_fdata().squeeze()
    data.append(
        nsd.fit(
            subjix,
            'lh.white',
            'fsaverage',
            a1,
            badval=0
        )
    )
data = np.asarray(data)

# Write out the results to an .mgz file.
fsdir = os.path.join(nsd_dir, 'freesurfer', 'fsaverage')
nsd_write_fs(
    data,
    'lh.testG.mgz',
    fsdir)

# Inspect on fsaverage's lh.inflated surface:
#   lh.testG.mgz
# Confirm that the subjects are reasonably well aligned.

# test case for polar angle data
subjix = 1
sourcedata = f'{nsd_dir}/freesurfer/subj{subjix:02d}/label/lh.prfangle.mgz'
sourcespace = 'lh.white'
targetspace = 'fsaverage'
nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype='cubic',
    badval=0,
    outputfile='lh.testH.mgz',
    fsdir=fsdir)
# Map surface-oriented results to volume space.

# Here take the Kastner2015 atlas (as prepared in the native subject surface's
# space), associate it with the vertices of the three cortical depth surfaces,
# and use a winner-take-all approach to convert these surface data to a 0.8-mm
# volume.
# Notice that this demonstrates the ability to aggregate data across left
# and right hemispheres before converting to a volume.

subjix = 1

sourcedata = np.r_[
    np.tile(
        f'{nsd_dir}/freesurfer/subj{subjix:02d}/label/lh.Kastner2015.mgz', 3),
    np.tile(
        f'{nsd_dir}/freesurfer/subj{subjix:02d}/label/rh.Kastner2015.mgz', 3)
        ].tolist()

sourcespace = [
    'lh.layerB1',
    'lh.layerB2',
    'lh.layerB3',
    'rh.layerB1',
    'rh.layerB2',
    'rh.layerB3'
    ]
targetspace = 'anat0pt8'
nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype='surfacewta',
    badval=-1,
    outputfile='testH.nii.gz')

# Inspect the results by comparing the following:
#   ppdata/subj01/anat/T1_0pt8_masked.nii.gz
#   testH.nii.gz

# Now that we have the atlas in the subject's anatomical space, we can now
# create a version that is in the subject's functional space.
sourcespace = 'anat0pt8'
targetspace = 'func1pt0'
sourcedata = 'testH.nii.gz'
nsd.fit(
    subjix,
    sourcespace,
    targetspace,
    sourcedata,
    interptype='wta',
    badval=-1,
    outputfile='testI.nii.gz')

# Inspect the results by comparing the following:
#   ppdata/subj01/func1mm/mean.nii.gz
#   testI.nii.gz
