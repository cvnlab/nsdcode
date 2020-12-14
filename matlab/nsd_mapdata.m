function transformeddata = nsd_mapdata(subjix,sourcespace,targetspace,sourcedata,interptype,badval,outputfile,outputclass,fsdir)

% function transformeddata = nsd_mapdata(subjix,sourcespace,targetspace,sourcedata,interptype,badval,outputfile,outputclass,fsdir)
%
% <subjix> is the subject number 1-8
% <sourcespace> is a string indicating the source space (where the data currently are)
% <targetspace> is a string indicating the target space (where the data need to go)
% <sourcedata> is:
%   (1) one or more 3D volumes (X x Y x Z x D)
%   (2) a .nii or .nii.gz file with one or more 3D volumes
%   (3) one or more surface vectors (V x D)
%   (4) a .mgz file with one or more surface vectors
% <interptype> (optional) is 'nearest' | 'linear' | 'cubic'. Default: 'cubic'.
%   Special cases are 'wta' and 'surfacewta' (more details below).
% <badval> (optional) is the value to use for invalid locations. Default: NaN.
% <outputfile> (optional) is:
%   (1) a file.nii or file.nii.gz file to write to
%   (2) a [lh,rh].file.[mgz,mgh] file to write to
%   Default is [] which means to not write out a file.
% <outputclass> (optional) is the output format to use (e.g. 'single').
%   Default is to use the class of <sourcedata>. Note that we always perform
%   calculations in double format and then convert at the end.
% <fsdir> (optional) is the FreeSurfer subject directory for the <targetspace>, like
%   '/path/to/subj%02d' or '/path/to/fsaverage'. We automatically sprintf
%   the <subjix> into <fsdir>. This input is needed only when writing .mgz files.
%
% There are four types of use-cases:
%
% (1) volume-to-volume
%     This includes [anat* | func* | MNI] -> [anat* | func* | MNI].
%     Note that within-space transforms are implemented for anat (e.g. anat1pt0 to anat0pt8),
%     but not for func.
%
% (2) volume-to-nativesurface
%     This includes [anat* | func* | MNI] -> [white | pial | layerB1 | layerB2 | layerB3].
%
% (3) nativesurface-to-fsaverage  or  fsaverage-to-nativesurface
%     This includes [white] -> [fsaverage] and
%                   [fsaverage] -> [white].
%     In this case, note that nearest-neighbor is always used (<interptype> is ignored).
%
% (4) nativesurface-to-volume
%     This includes [white | pial | layerB1 | layerB2 | layerB3] -> [anat*]
%     In this case, a linear weighting scheme is always used, unless you specify
%     <interptype> as 'surfacewta' which means to treat each dataset as containing
%     discrete integers and perform a winner-take-all voting mechanism (this is useful
%     for label data). Also, it is possible to supply data defined on multiple
%     surfaces (e.g. layerB1 + layerB2 + layerB3) that are collectively mapped to
%     volume. To do this, you should supply <sourcespace> as a cell vector of strings 
%     and supply <sourcedata> as a cell vector of things like cases (3) or (4) as
%     described for <sourcedata> (see above). Note that it is okay to combine data
%     defined on lh and rh surfaces!
%
% The valid strings for source and target spaces are:
%   'anat0pt5'
%   'anat0pt8'
%   'anat1pt0'
%   'func1pt0'
%   'func1pt8'
%   'MNI'
%   '[lh,rh].white'
%   '[lh,rh].pial'
%   '[lh,rh].layerB1'
%   '[lh,rh].layerB2'
%   '[lh,rh].layerB3'
%   'fsaverage'
%
% Map data from one space to another space. The data in the input variable
% <sourcedata> is mapped and returned in the output variable <transformeddata>.
%
% Details on the weighting scheme used for case (4) above:
%   Each vertex contributes a linear kernel that has a size of exactly 2 x 2 x 2 voxels
% (at whatever the target anatomical resolution is). All of the linear kernels are added
% up, and values are obtained at the center of each volumetric voxel. In other words,
% the value associated with each voxel is simply a weighted average of vertices that 
% are near that voxel (for example, within +/- 0.8 mm when targeting the anat0pt8 space).
% In the 'surfacewta' case, the integer labeling contributing the largest weight wins.
%
% Details on the 'wta' and 'surfacewta':
%   These schemes are winner-take-all schemes. The sourcedata must consist of discrete 
% integer labels. Each integer is separately mapped as a binary volume, and the integer
% resulting in the largest value at a given location is assigned to that location.
% This mechanism is useful for ROI labelings.

% inputs
if ~exist('interptype','var') || isempty(interptype)
  interptype = 'cubic';
end
if ~exist('badval','var') || isempty(badval)
  badval = NaN;
end
if ~exist('outputfile','var') || isempty(outputfile)
  outputfile = [];
end
if ~exist('outputclass','var') || isempty(outputclass)
  outputclass = [];
end
if ~exist('fsdir','var') || isempty(fsdir)
  fsdir = [];
end

% setup
tdir = sprintf('%s/ppdata/subj%02d/transforms',nsd_datalocation,subjix);

% figure out what case we are in
if isequal(sourcespace,'fsaverage') || isequal(targetspace,'fsaverage')
  casenum = 3;
elseif ismember(targetspace(1:3),{'lh.' 'rh.'})
  casenum = 2;
elseif iscell(sourcespace) || ismember(sourcespace(1:3),{'lh.' 'rh.'})
  casenum = 4;
else
  casenum = 1;
end

% deal with cell vector
if casenum==4
  if ~iscell(sourcespace)
    sourcespace = {sourcespace};
  end
  if ~iscell(sourcedata)
    sourcedata = {sourcedata};
  end
end

% deal with basic setup
switch casenum
case 1
  tfile = sprintf('%s/%s-to-%s.nii.gz',tdir,sourcespace,targetspace);
case {2 3}
  if ismember(targetspace(1:3),{'lh.' 'rh.'})
    hemi = targetspace(1:2);  % 'lh'
    tfile = sprintf('%s/%s.%s-to-%s.mgz',tdir,hemi,sourcespace,targetspace(4:end));
  else
    assert(ismember(sourcespace(1:3),{'lh.' 'rh.'}));
    hemi = sourcespace(1:2);  % 'lh'
    tfile = sprintf('%s/%s.%s-to-%s.mgz',tdir,hemi,sourcespace(4:end),targetspace);
  end
case 4
  tfile = {};
  for p=1:length(sourcespace)
    hemi = sourcespace{p}(1:2);  % 'lh'
    tfile{p} = sprintf('%s/%s.%s-to-%s.mgz',tdir,hemi,targetspace,sourcespace{p}(4:end));  % e.g. lh.anat0pt8-to-layerB1.mgz
  end
end

% for writing target volumes, we need to know the voxel size
switch targetspace
case 'anat0pt5'
  voxelsize = 0.5;
  res = 512;
case 'anat0pt8'
  voxelsize = 0.8;
  res = 320;
case 'anat1pt0'
  voxelsize = 1.0;
  res = 256;
case 'func1pt0'
  voxelsize = 1.0;
case 'func1pt8'
  voxelsize = 1.8;
case 'MNI'
  voxelsize = 1;
end

% do it for the source
if ~iscell(sourcespace)
  switch sourcespace
  case 'anat0pt5'
    sourcevoxelsize = 0.5;
  case 'anat0pt8'
    sourcevoxelsize = 0.8;
  case 'anat1pt0'
    sourcevoxelsize = 1.0;
  case 'func1pt0'
    sourcevoxelsize = 1.0;
  case 'func1pt8'
    sourcevoxelsize = 1.8;
  case 'MNI'
    sourcevoxelsize = 1;
  end
end

% load transform
switch casenum
case 1
  if exist(tfile,'file')  % anat-to-anat does not have files
    a1 = getfield(load_untouch_nii(tfile),'img');  % X x Y x Z x 3
  end
case {2 3}
  a1 = squish(load_mgh(tfile),3);                 % V x 3 (decimal coordinates) or V x 1 (index)
case 4
  a1 = [];
  for p=1:length(tfile)
    a1 = cat(1,a1,squish(load_mgh(tfile{p}),3));  % V-across-differentsurfaces x 3 (decimal coordinates)
  end
end

% load sourcedata
switch casenum
case {1 2 3}
  if ischar(sourcedata)
    if isequal(sourcedata(end-3:end),'.mgz')
      sourcedata = squish(load_mgh(sourcedata),3);                    % V x D
    else
      sourcedata = getfield(load_untouch_nii(sourcedata),'img');     % X x Y x Z x D
    end
  end
case 4
  temp = [];
  for p=1:length(sourcedata)
    if ischar(sourcedata{p})
      temp = cat(1,temp,squish(load_mgh(sourcedata{p}),3));    % V-across-differentsurfaces x D
    else
      temp = cat(1,temp,sourcedata{p});
    end
  end
  sourcedata = temp;
  clear temp;
end
sourceclass = class(sourcedata);

% deal with outputclass
if isempty(outputclass)
  outputclass = sourceclass;
end

% do it
switch casenum
case 1    % volume-to-volume

  % handle within-space transforms specially
  if ~isempty(regexp(sourcespace,'^anat')) && ~isempty(regexp(targetspace,'^anat'))
    
    % process each volume, relying heavily on changevolumeres
    transformeddata = cast([],outputclass);
    for p=size(sourcedata,4):-1:1
%      fprintf('working on volume %d of %d.\n',p,size(sourcedata,4));
      transformeddata(:,:,:,p) = changevolumeres(sourcedata(:,:,:,p),repmat(sourcevoxelsize,[1 3]),repmat(res,[1 3]),isequal(interptype,'wta'));
    end
    
  % otherwise, this is the standard case
  else

    % construct coordinates
    coords = [flatten(a1(:,:,:,1)); flatten(a1(:,:,:,2)); flatten(a1(:,:,:,3));];
    coords(coords==9999) = NaN;  % ensure that 9999 locations will propagate as NaN

    % interpolate, fill the bad values, and set the output class
    transformeddata = cast([],outputclass);
    for p=size(sourcedata,4):-1:1
%      fprintf('working on volume %d of %d.\n',p,size(sourcedata,4));
      transformeddata(:,:,:,p) = cast(nanreplace(reshape(ba_interp3_wrapper(sourcedata(:,:,:,p), ...
                                      coords,interptype),sizefull(a1,3)),badval),outputclass);
    end

  end

  % if user wants a file, write it out
  if ~isempty(outputfile)
    if isequal(targetspace,'MNI')
      % in the case of the target being MNI, we are going to write out LPI NIFTIs.
      % so, we have to flip the first dimension so that the first voxel is indeed
      % Left. also, in ITK-SNAP, the MNI template has world (ITK) coordinates at
      % (0,0,0) which corresponds to voxel coordinates (91,127,73). These voxel
      % coordinates are relative to RPI. So, for the origin of our LPI file that
      % we will write, we need to make sure that we "flip" the first coordinate.
      % The MNI volume has dimensions [182 218 182], so we subtract the first
      % coordinate from 183.
      transformeddata = flipdim(transformeddata,1);  % now, it's in LPI
      origin = [183-91 127 73];
    else
      origin = [];
    end
    nsd_savenifti(transformeddata,repmat(voxelsize,[1 3]),outputfile,[],origin);
  end

case 2    % volume-to-nativesurface

  % construct coordinates
  coords = [flatten(a1(:,1)); flatten(a1(:,2)); flatten(a1(:,3));];
  coords(coords==9999) = NaN;  % ensure that 9999 locations will propagate as NaN

  % interpolate, fill the bad values, and set the output class
  transformeddata = cast([],outputclass);
  for p=size(sourcedata,4):-1:1
%    fprintf('working on volume %d of %d.\n',p,size(sourcedata,4));
    transformeddata(:,p) = cast(nanreplace(ba_interp3_wrapper(sourcedata(:,:,:,p), ...
                                    coords,interptype),badval),outputclass);
  end

  % if user wants a file, write it out
  if ~isempty(outputfile)
    nsd_savemgz(transformeddata,outputfile,sprintf(fsdir,subjix));
  end

case 3    % nativesurface-to-fsaverage  or  fsaverage-to-nativesurface

  % use nearest-neighbor and set the output class
  transformeddata = cast(sourcedata(a1,:),outputclass);
  
  % if user wants a file, write it out
  if ~isempty(outputfile)
    nsd_savemgz(transformeddata,outputfile,sprintf(fsdir,subjix));
  end

case 4

  % do stuff
  transformeddata = cast(cvnmapsurfacetovolume_helper(sourcedata.',a1.',res,isequal(interptype,'surfacewta'),badval),outputclass);
  
  % if user wants a file, write it out
  if ~isempty(outputfile)
    nsd_savenifti(transformeddata,repmat(voxelsize,[1 3]),outputfile);
  end
  
end
