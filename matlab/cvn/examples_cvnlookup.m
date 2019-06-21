%% This document demonstrates basic usage of cvnlookup.m (which is a wrapper for cvnlookupimages.m).

% Note that cvnlookup.m requires the cvncode github repository.


%% Example use of cvnlookup.m

% We need to make sure the FreeSurfer subjects directory is set correctly
setenv('SUBJECTS_DIR','/home/surly-raid4/kendrick-data/nsd/nsddata/freesurfer');

% Let's visualize the Kastner2015 atlas on subj01
data = [nsd_datalocation '/freesurfer/subj01/label/lh.Kastner2015.mgz'];
cvnlookup('subj01',1,data,[0 25],jet(256),0.5);

% Note that we automatically get some variables (rawimg,Lookup,rgbimg,himg) 
% assigned to the workspace.

% We can directly call imagesc on rawimg.
figure; imagesc(rawimg,[0 25]); colormap(jet(256)); axis image;


%% Draw an ROI

% Let's call cvnlookup again and explicitly get the outputs
[rawimg,Lookup,rgbimg,himg] = cvnlookup('subj01',1,data,[0 25],jet(256),0.5);

% Manually draw an ROI on the left hemisphere.
% Note: drawing is valid only on spherical surfaces.
Rmask = drawroipoly(himg,Lookup);

% Rmask is a (numlh+numrh)x1 binary mask
size(Rmask)

% Let's visualize the ROI in order to check it
extraopts = {'roicolor','k','roimask',Rmask};
cvnlookup('subj01',1,data,[0 25],jet(256),0.5,[],[],extraopts);

% We can also directly visualize the ROI as if it were data
cvnlookup('subj01',1,Rmask,[0 1],gray);


%% Save the ROI

% This is a little tricky because the ROI data reflects
% both hemispheres concatenated.

% First, create a valstruct and put the ROI inside it
valstruct = valstruct_create('subj01');
valstruct = setfield(valstruct,'data',Rmask);

% Now, we can save an .mgz file
fsdir = [nsd_datalocation '/freesurfer/subj01'];
nsd_savemgz(valstruct_getdata(valstruct,'lh'),'lh.testA.mgz',fsdir);

% Addendum: lh.testA.mgz can be fed back as data into cvnlookup (even though it is just
% one hemisphere, the code automatically fills in NaNs for the other hemisphere).
