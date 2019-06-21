%% This document demonstrates quick-and-dirty usage of cvnlookup.m.

% here we start with volume-oriented data, do a quick mapping to the
% mid-gray surface, and then use cvnlookup.m to visualize the results.
sourcedata = sprintf('%s/ppdata/subj01/func1mm/R2.nii.gz',nsd_datalocation);
data =  nsd_mapdata(1,'func1pt0','lh.layerB2',sourcedata,'linear');
data2 = nsd_mapdata(1,'func1pt0','rh.layerB2',sourcedata,'linear');
cvnlookup('subj01',1,[data; data2],[0 50],hot(256));
