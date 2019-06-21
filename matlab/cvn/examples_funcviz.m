%% This document shows how cvnlookup.m can be used to generate basic
%% surface inspections of functional results for the NSD subjects.

% We plot the following quantities:
%   (1) mean (average EPI intensity)
%   (2) onoffbeta (BOLD percent signal change for a GLM incorporating
%                  a single ON-OFF regressor)
%   (3) valid (percentage of scan sessions where data were present)
%   (4) R2 (variance explained by the 'betas_fithrf_GLMdenoise_RR' GLM model)
% All visualizations are performed using the fsaverage flat surface.
% See below for details on how the resampling is performed.


%% Load volume-oriented results and map to surface

% Our strategy is to: load results from the 1-mm preparation, map
% these to the 3 subject-native depth surfaces using nearest-neighbor,
% average across depth, and then map to fsaverage (using nearest-neighbor).
% Each [lh,rh].XXX.mgz file that we write will consist of 9 maps corresponding
% to the results from the 8 subjects and the mean across subjects.

% define
dirs = {sprintf('%s/ppdata/subj%%02d/func1mm/',nsd_datalocation) ...
        sprintf('%s/ppdata/subj%%02d/func1mm/betas_fithrf_GLMdenoise_RR/',nsd_datalocation('betas'))};
files = {{'mean' 'onoffbeta' 'valid'} {'R2'}};
hemis = {'lh' 'rh'};
fsdir =    [nsd_datalocation '/freesurfer/subj%02d'];
fsdiravg = [nsd_datalocation '/freesurfer/fsaverage'];
nsubj = 8;
ndepth = 3;
outputdir = sprintf('%s/results/',nsd_datalocation);

% do it
for dd=1:length(dirs)
  for ff=1:length(files{dd})
    for hh=1:length(hemis)

      % init data0 (V x maps)
      data0 = [];
      for ss=1:nsubj

        % load data
        sourcedata = sprintf('%s/%s.nii.gz',sprintf(dirs{dd},ss),files{dd}{ff});
        a1 = getfield(load_untouch_nii(sourcedata),'img');

        % map data to subject-native surfaces (nearest-neighbor, conversion to single) and average across depth.
        data1 = [];
        for ii=1:ndepth
          data1(:,:,ii) = nsd_mapdata(ss,'func1pt0',sprintf('%s.layerB%d',hemis{hh},ii),a1,'nearest',[],[],'single');
        end
        data1 = mean(data1,3);

        % map from subject-native surface to fsaverage
        data0 = cat(2,data0,nsd_mapdata(ss,sprintf('%s.white',hemis{hh}),'fsaverage',data1,[],[],[],'single'));

      end

      % create a group-average version
      data0(:,end+1) = mean(data0,2);

      % save
      nsd_savemgz(data0,sprintf('%s/%s.%s.mgz',outputdir,hemis{hh},files{dd}{ff}),fsdiravg);

    end
  end
end


%% Take surface-oriented results and generate visualizations

% define
subjs = {'subj01' 'subj02' 'subj03' 'subj04' 'subj05' 'subj06' 'subj07' 'subj08' 'fsaverage'};
files = ...
...% name        color range    color map         transform function            threshold
  {{'mean'       [0 1]          gray(256)         @(x)(posrect(x)/4095).^.5     []} ...
   {'onoffbeta'  [-8 8]         cmapsign4(256)    []                            1*j} ...
   {'valid'      [0 1]          jet(256)          []                            []} ...
   {'R2'         [0 1]          hot(256)          @(x)(posrect(x)/100).^.5      (20/100).^.5}};

% do it
for ff=1:length(files)

  % load data file and transform
  inputfile = sprintf('%s/??.%s.mgz',outputdir,files{ff}{1});
  data = cvnloadmgz(inputfile);
  if ~isempty(files{ff}{4})
    data = feval(files{ff}{4},data);
  end

  % visualize each dataset
  Lookup = [];
  for p=1:size(data,4)

    outputfile = sprintf([nsd_datalocation '/figures/fsaverageflat_%s_%03d.png'],files{ff}{1},p);
    [rawimg,Lookup,rgbimg,himg] = cvnlookup('fsaverage',10,data(:,1,1,p),files{ff}{2},files{ff}{3},[],Lookup,0);
    imwrite(rgbimg,outputfile);

    if ~isempty(files{ff}{5})
      outputfile = sprintf([nsd_datalocation '/figures/fsaverageflat_%s_thresh_%03d.png'],files{ff}{1},p);
      [rawimg,Lookup,rgbimg,himg] = cvnlookup('fsaverage',10,data(:,1,1,p),files{ff}{2},files{ff}{3},files{ff}{5},Lookup,0);
      imwrite(rgbimg,outputfile);
    end

  end

end
