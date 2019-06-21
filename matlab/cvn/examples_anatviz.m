%% This document shows how cvnlookup.m can be used to generate basic
%% surface inspections of anatomical results for the NSD subjects.

% We plot curvature, the Kastner2015 atlas, the HCP_MMP1.0 atlas,
% and the visualsulc atlas. All surface visualizations are of
% the fsaverage flat surface. For individual NSD subjects, curvature
% values are automatically transferred (by cvnlookup.m) using 
% nearest-neighbor to the fsaverage surface, which allows individual-subject
% data to be viewed in the common fsaverage space. Note that atlases are
% originally defined on the fsaverage surface, so we can just plot these
% for the 'fsaverage' subject.

% define
subjs = {'subj01' 'subj02' 'subj03' 'subj04' 'subj05' 'subj06' 'subj07' 'subj08' 'fsaverage'};
  %          name          color range   color map           threshold
atlases = {{'Kastner2015'  [0 25]        jet(256)            0.5} ...
           {'HCP_MMP1'     [-.5 180.5]   colormap_hcp_mmp()  0.5} ...
           {'visualsulc'   [0 14]        jet(256)            0.5}};
hemis = {'lh' 'rh'};

% do it
for p=1:length(subjs)
  subjectid = subjs{p};
  
  %% CURVATURE

  % define
  inputfile = sprintf([nsd_datalocation '/freesurfer/%s/surf/??.curvature.mgz'],subjectid);
  outputfile = sprintf([nsd_datalocation '/figures/fsaverageflat_curvature_%s.png'],subjectid);
  
  % load data (V x 1)
  data = cvnloadmgz(inputfile);

  % perform lookup and save to .png file
  [rawimg,Lookup,rgbimg,himg] = cvnlookup(subjectid,10,data < 0,[-1 2],gray(256),[],[],0);
  imwrite(rgbimg,outputfile);

  %% ATLASES
  
  if p==length(subjs)  % process atlases only for the fsaverage subject

  for q=1:length(atlases)

    % define
    inputfile = sprintf([nsd_datalocation '/freesurfer/%s/label/??.%s.mgz'],subjectid,atlases{q}{1});
    outputfile = sprintf([nsd_datalocation '/figures/fsaverageflat_%s_%s.png'],atlases{q}{1},subjectid);
    outputfile2 = sprintf([nsd_datalocation '/figures/fsaverageflat_%s_names_%s.png'],atlases{q}{1},subjectid);

    % load data (V x 1)
    data = cvnloadmgz(inputfile);

    % perform lookup and save to .png file
    [rawimg,Lookup,rgbimg,himg] = cvnlookup(subjectid,10,data,atlases{q}{2},atlases{q}{3},atlases{q}{4},[],0);
    imwrite(rgbimg,outputfile);
  
    % add roinames and save to another .png file
    [~,roinames,~] = cvnroimask(subjectid,hemis,[atlases{q}{1} '*'],[],'orig','cell');
    roinames = regexprep(roinames{1},'@.+','');
    rgbimg = drawroinames(rawimg,rgbimg,Lookup,1:numel(roinames),cleantext(roinames));
    imwrite(rgbimg,outputfile2);
  
  end
  
  end

end
