%% This document demonstrates a simple analysis of the NSD data from start to finish.


%% LOAD DATA

% define
nsess = 6;                                % how many sessions of data to load in?
whichglm = 'betas_fithrf_GLMdenoise_RR';  % which GLM results to load?
roilabels = {'V1v' 'V1d' 'V2v' 'V2d' 'V3v' 'V3d' 'hV4' 'VO1' 'VO2' 'PHC1' 'PHC2' 'TO2' 'TO1' 'LO2' 'LO1' 'V3b' 'V3a' 'IPS0' 'IPS1' 'IPS2' 'IPS3' 'IPS4' 'IPS5' 'SPL1' 'FEF'};
outputdir = sprintf('%s/figures/pca/',nsd_datalocation); mkdirquiet(outputdir);

% load data
volsize = {};  % each is [X Y Z]
voxelix = {};  % each is voxels x 1 with indices into the 3D volume (voxels we will analyze)
rois = {};     % each is X x Y x Z with ROI labelings (-1 = not brain, 0 = not labeled, 1-25 = ROIs)
betas = {};    % each is voxels x 750 trials x sessions
r2 = {};       % each is voxels x 1
for subjix=1:8, subjix

  % determine voxels in the nsdgeneral ROI
  roifile = sprintf('%s/ppdata/subj%02d/func1pt8mm/roi/nsdgeneral.nii.gz',nsd_datalocation,subjix);
  a1 = load_untouch_nii(roifile);
  volsize{subjix} = size(a1.img);
  voxelix{subjix} = find(a1.img == 1);                  % this is a vector of indices into the 3D volume
  [d1,d2,d3,ii] = computebrickandindices(a1.img == 1);  % this is a brick subrange and indices into that brick

  % load in ROI labelings
  roifile = sprintf('%s/ppdata/subj%02d/func1pt8mm/roi/Kastner2015.nii.gz',nsd_datalocation,subjix);
  a1 = load_untouch_nii(roifile);
  rois{subjix} = a1.img;

  % load beta weights from each session
  for sess=1:nsess, sess
    betafile = sprintf('%s/ppdata/subj%02d/func1pt8mm/%s/betas_session%02d.mat', ...
                       nsd_datalocation('betas'),subjix,whichglm,sess);
    a0 = matfile(betafile);
    betas{subjix}(:,:,sess) = single(subscript(squish(a0.betas(d1,d2,d3,:),3),{ii ':'}))/300;
  end

  % load session-averaged R2 values
  r2file = sprintf('%s/ppdata/subj%02d/func1pt8mm/%s/R2.nii.gz', ...
                   nsd_datalocation('betas'),subjix,whichglm);
  a0 = load_untouch_nii(r2file);
  r2{subjix} = vflatten(a0.img(voxelix{subjix}));

end


%% ANALYZE DATA

% perform PCA and save the first three PCs
pcs = {};
for subjix=1:8, subjix

  % z-score and then concatenate across sessions (750*sess x voxels)
  data0 = squish(permute(calczscore(betas{subjix},2),[2 3 1]),2);
  
  % some voxels have NaNs after z-scoring (because all betas are 0, due to missing data)
  data0(isnan(data0)) = 0;
  
  % PCA
  [u,s,v] = svd(data0,0);
  
  % save first 3 PCs
  pcs{subjix} = v(:,1:3);  % voxels x 3
  
  % clean up
  clear data0 u s v;

end


%% VISUALIZE MAPS

% visualize qualitative results (surface maps)
for subjix=1:8

  Lookup = [];
  for pp=1:3

    % define the data we want to visualize
    vals = pcs{subjix}(:,pp);
    mx = max(abs(vals));
  
    % reconstitute a 3D volume
    vol = -1000*ones(volsize{subjix});
    vol(voxelix{subjix}) = vals;

    % map from volume to surface (mid-gray) and visualize the results on fsaverage flat
    data =  nsd_mapdata(subjix,'func1pt8','lh.layerB2',vol,'nearest');
    data2 = nsd_mapdata(subjix,'func1pt8','rh.layerB2',vol,'nearest');
    extraopt = {'roiname','Kastner*','roicolor','w'};
    [rawimg,Lookup,rgbimg,himg] = cvnlookup(sprintf('subj%02d',subjix),10,[data; data2],[-mx mx],cmapsign4(256),-999,Lookup,0,extraopt);
    imwrite(rgbimg,sprintf('%s/subj%02d_pc%02d.png',outputdir,subjix,pp));

  end

end


%% QUANTIFY RESULTS USING ROIS

% quantify results
results = [];  % subjects x pcs x rois
for subjix=1:8
  for pp=1:3
    for rr=1:length(roilabels)
      ix = ismember(voxelix{subjix},find(rois{subjix}==rr));
      results(subjix,pp,rr) = mean(pcs{subjix}(ix,pp));
    end
  end
end


%% MAKE FIGURE SHOWING ROI RESULTS

% visualize quantitative results (ROIs)
figureprep([100 100 1300 1000]); hold on;
for subjix=1:8
  subplot(8,1,subjix); hold on;
  bar(squish(results(subjix,:,:),2)');
  set(gca,'XTick',1:length(roilabels));
  set(gca,'XTickLabel',roilabels);
end
figurewrite('results',[],[],outputdir);
