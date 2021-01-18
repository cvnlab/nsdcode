%% This document shows several examples of how to use nsd_mapdata.m.

% NIFTI files can be viewed in ITK-SNAP.
% MGZ files can be viewed using FreeSurfer's freeview.


%% Setup path

addpath(genpath('/home/adf/charesti/Documents/GitHub/nsdcode/matlab'))


%% Map T1 anatomical to EPI space

% Here we map the 0.8-mm T1 to the 1-mm EPI space using cubic interpolation.
% The resulting T1 volume might be useful for viewing volume-based
% fMRI results against the anatomy.
subjix = 1;
sourcedata = sprintf('%s/ppdata/subj%02d/anat/T1_0pt8_masked.nii.gz',nsd_datalocation,subjix);  
nsd_mapdata(subjix,'anat0pt8','func1pt0',sourcedata,'cubic',0,'testA.nii.gz');

% To confirm correctness, compare the following:
%   testA.nii.gz
%   ppdata/subj01/func1mm/mean.nii.gz


%% Map EPI results to MNI space

% Here we take the variance explained (R2) value obtained for the "betas_fithrf_GLMdenoise_RR"
% GLM model in the first NSD session in the high-resolution 1-mm functional preparation,
% and map this to MNI space (which has 1-mm resolution).
subjix = 1;
sourcedata = sprintf('%s/ppdata/subj%02d/func1mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz',nsd_datalocation('betas'),subjix);  
nsd_mapdata(subjix,'func1pt0','MNI',sourcedata,'cubic',0,'testB_1mm.nii.gz');

% For comparison, we repeat the same operation but for the low-resolution
% 1.8-mm functional preparation.
sourcedata = sprintf('%s/ppdata/subj%02d/func1pt8mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz',nsd_datalocation('betas'),subjix);  
nsd_mapdata(subjix,'func1pt8','MNI',sourcedata,'cubic',0,'testB_1pt8mm.nii.gz');

% To assess the results, compare the following:
%   templates/MNI152_T1_1mm.nii.gz
%   testB_1mm.nii.gz
%   testB_1pt8mm.nii.gz
% Notice that the high- vs. low-resolution functional preparation makes a difference.

% To confirm sanity of the transformations, we can repeat the transformations for the
% mean EPI volume in the two different functional preparations.
sourcedata = sprintf('%s/ppdata/subj%02d/func1mm/mean_session01.nii.gz',nsd_datalocation,subjix);  
nsd_mapdata(subjix,'func1pt0','MNI',sourcedata,'cubic',0,'testC_1mm.nii.gz');
sourcedata = sprintf('%s/ppdata/subj%02d/func1pt8mm/mean_session01.nii.gz',nsd_datalocation,subjix);  
nsd_mapdata(subjix,'func1pt8','MNI',sourcedata,'cubic',0,'testC_1pt8mm.nii.gz');

% Compare the above results to:
%   testC_1mm.nii.gz
%   testC_1pt8mm.nii.gz
% Notice that the two mean EPI volumes are spatially consistent but differ in
% the level of spatial detail.


%% Map EPI results to surface space

% Here we take the same variance explained (R2) value described above
% and map it to the mid-gray native subject surface in the left hemisphere.
% This mapping is accomplished using a cubic interpolation of the data
% at each surface vertex location.
subjix = 1;
fsdir = [nsd_datalocation '/freesurfer/subj%02d'];
sourcedata = sprintf('%s/ppdata/subj%02d/func1mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz',nsd_datalocation('betas'),subjix);  
nsd_mapdata(subjix,'func1pt0','lh.layerB2',sourcedata,'cubic',0,'lh.testD_layerB2.mgz',[],fsdir);

% Let's repeat the same operation but sample the data onto the other two surfaces.
% "layerB1", "layerB2", and "layerB3" correspond to 25%, 50%, and 75%
% of the distance from the pial to the white-matter surfaces, respectively.
nsd_mapdata(subjix,'func1pt0','lh.layerB1',sourcedata,'cubic',0,'lh.testD_layerB1.mgz',[],fsdir);
nsd_mapdata(subjix,'func1pt0','lh.layerB3',sourcedata,'cubic',0,'lh.testD_layerB3.mgz',[],fsdir);

% To assess the results, compare the following on the lh.inflated surface:
%   lh.testD_layerB1.mgz
%   lh.testD_layerB2.mgz
%   lh.testD_layerB3.mgz
% Notice that the results depend substantially on the surface onto which the data are sampled.

% We can map multiple datasets in one call to nsd_mapdata.m. In the following example,
% the file "R2run_session01.nii.gz" contains 12 different R2 values, one for each
% of the 12 runs conducted in the first NSD session. Each volume is independently
% mapped onto the lh.layerB2 surface, and the multiple surface-based outputs
% are saved into a single .mgz file.
sourcedata = sprintf('%s/ppdata/subj%02d/func1mm/betas_fithrf_GLMdenoise_RR/R2run_session01.nii.gz',nsd_datalocation('betas'),subjix);  
nsd_mapdata(subjix,'func1pt0','lh.layerB2',sourcedata,'cubic',0,'lh.testE.mgz',[],fsdir);

% We can also perform the mapping and omit having to write out a file to disk.
% Instead, we obtain the results in our workspace.
data = nsd_mapdata(subjix,'func1pt0','lh.layerB2',sourcedata,'cubic',0);
figure; plot(median(data,1)); xlabel('Run number'); ylabel('Median R2');
%%


%% Map native subject surface results to fsaverage

% Here we repeat the mapping for variance explained (R2) for the three cortical depths,
% accruing results in the workspace.
subjix = 1;
sourcedata = sprintf('%s/ppdata/subj%02d/func1mm/betas_fithrf_GLMdenoise_RR/R2_session01.nii.gz',nsd_datalocation('betas'),subjix);  
data = [];
for p=1:3
  data(:,p) = nsd_mapdata(subjix,'func1pt0',sprintf('lh.layerB%d',p),sourcedata,'cubic',0);
end

% Now we average results across the three cortical depths and use nearest-neighbor
% interpolation to bring the result to fsaverage. (Mapping to/from fsaverage always
% involves nearest-neighbor interpolation, so we just use [] for <interptype>.)
fsdir = [nsd_datalocation '/freesurfer/fsaverage'];
nsd_mapdata(subjix,'lh.white','fsaverage',mean(data,2),[],0,'lh.testF.mgz',[],fsdir);

% Assess the results by inspecting on fsaverage's lh.inflated surface:
%   lh.testF.mgz
% and comparing this to the native subject's lh.inflated surface:
%   lh.testD_layerB2.mgz


%% Inspect alignment of subjects to fsaverage

% Here we load each subject's native curvature and map it to fsaverage.
data = [];
for subjix=1:8
  a1 = read_curv(sprintf('%s/freesurfer/subj%02d/surf/lh.curv',nsd_datalocation,subjix));
  data(:,subjix) = nsd_mapdata(subjix,'lh.white','fsaverage',a1,[],0);
end

% Write out the results to an .mgz file.
fsdir = [nsd_datalocation '/freesurfer/fsaverage'];
nsd_savemgz(data,'lh.testG.mgz',fsdir);

% Inspect on fsaverage's lh.inflated surface:
%   lh.testG.mgz
% Confirm that the subjects are reasonably well aligned.


%% Map surface-oriented results to volume space.

% Here take the Kastner2015 atlas (as prepared in the native subject surface's space),
% associate it with the vertices of the three cortical depth surfaces, and use
% a winner-take-all approach to convert these surface data to a 0.8-mm volume.
% Notice that this demonstrates the ability to aggregate data across left and right
% hemispheres before converting to a volume.
subjix = 1;
sourcedata = [repmat({sprintf('%s/freesurfer/subj%02d/label/lh.Kastner2015.mgz',nsd_datalocation,subjix)},[1 3]) ...
              repmat({sprintf('%s/freesurfer/subj%02d/label/rh.Kastner2015.mgz',nsd_datalocation,subjix)},[1 3])];
nsd_mapdata(subjix,{'lh.layerB1' 'lh.layerB2' 'lh.layerB3' ...
                    'rh.layerB1' 'rh.layerB2' 'rh.layerB3'},'anat0pt8',sourcedata,'surfacewta',-1,'testH.nii.gz');

% Inspect the results by comparing the following:
%   ppdata/subj01/anat/T1_0pt8_masked.nii.gz
%   testH.nii.gz

% Now that we have the atlas in the subject's anatomical space, we can now
% create a version that is in the subject's functional space.
nsd_mapdata(subjix,'anat0pt8','func1pt0','testH.nii.gz','wta',-1,'testI.nii.gz');  % changed from 'nearest' to 'wta'

% Inspect the results by comparing the following:
%   ppdata/subj01/func1mm/mean.nii.gz
%   testI.nii.gz

