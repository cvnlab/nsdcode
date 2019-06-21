function nsd_savemgz(data,file0,fsdir)

% function nsd_savemgz(data,file0,fsdir)
%
% <data> is V x D (where D >= 1) with surface data for one or more datasets.
%   No matter what format <data> is in, it appears that FreeSurfer always
%   writes .mgz files in single (float, 32-bit) format.
% <file0> is the path to a .mgz file to write. This file must conform to
%   the format [lh,rh].XXX.mgz.
% <fsdir> is the path to the FreeSurfer subject directory.
%
% Save MGZ file.

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
v = size(data,1);
d = size(data,2);

% sanity check
if v==1
  error('<data> should have surface data oriented along the columns');
end

% mangle fields
fsmgh.fspec = file0;
fsmgh.vol = reshape(data,1,v,1,d);  % 1 x V x 1 x D
fsmgh.volsize = [1 v 1];
fsmgh.height = 1;
fsmgh.width = v;
fsmgh.depth = 1;
fsmgh.nframes = d;
fsmgh.nvoxels = v;

% write
MRIwrite(fsmgh,file0);
