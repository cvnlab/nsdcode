function nsd_savemgz(data,file0,fsdir,numdepth)

% function nsd_savemgz(data,file0,fsdir,numdepth)
%
% <data> is V x D (where D >= 1) with surface data for one or more datasets.
%   Can also be V x DEPTH x D where DEPTH > 1. In this case, <numdepth> should
%   be supplied. No matter what format <data> is in, it appears that FreeSurfer 
%   always writes .mgz files in single (float, 32-bit) format.
% <file0> is the path to a .mgz (or .mgh) file to write. This file must conform to
%   the format [lh,rh].XXX.[mgz,mgh].
% <fsdir> is the path to the FreeSurfer subject directory.
% <numdepth> (optional) is the number of depths. Default: 1.
%
% Save MGZ file or MGH file (uncompressed).

% inputs
if ~exist('numdepth','var') || isempty(numdepth)
  numdepth = 1;
end

% ensure directory exists
mkdirquiet(stripfile(file0));

% determine hemi
filename0 = stripfile(file0,1);
hemi = filename0(1:2);
assert(ismember(hemi,{'lh' 'rh'}));

% load template
mgh0 = sprintf('%s/surf/%s.w-g.pct.mgh',fsdir,hemi);
if ~exist(mgh0,'file')  % fsaverage doesn't have the above file, so let's use this one:
  mgh0 = sprintf('%s/surf/%s.orig.avg.area.mgh',fsdir,hemi);
end
fsmgh = MRIread(mgh0);

% calc
if numdepth==1
  v = size(data,1);
  d = size(data,2);
else
  v = size(data,1);
  d = size(data,3);
end

% sanity check
if v==1
  error('<data> should have surface data oriented along the columns');
end

% mangle fields
fsmgh.fspec = file0;
fsmgh.vol = reshape(data,1,v,numdepth,d);  % 1 x V x numdepth x D
fsmgh.volsize = [1 v numdepth];
fsmgh.height = 1;
fsmgh.width = v;
fsmgh.depth = numdepth;
fsmgh.nframes = d;
fsmgh.nvoxels = v;

% write
MRIwrite(fsmgh,file0);
