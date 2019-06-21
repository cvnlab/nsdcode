function nsd_savenifti(data,res,file0,tr,origin)

% function nsd_savenifti(data,res,file0,tr,origin)
% 
% <data> is X x Y x Z x D (where D >= 1) with volume data
%   for one or more datasets. Can be of a specific format
%   like 'double' or 'int16'.
% <res> is [A B C] in millimeters for the voxel size
% <file0> is the path to a .nii.gz (or .nii) file to write.
%   If .gz extension is used, we do the gzip.
% <tr> (optional) is the TR in seconds.
%   Default is 1.
% <origin> (optional) is the origin to use.
%   Default is exact center of the volume slab.
%
% Save NIFTI file.

% input
if ~exist('tr','var') || isempty(tr)
  tr = [];
end
if ~exist('origin','var') || isempty(origin)
  origin = [];
end

% deal with file extension
wantgz = isequal(file0(end-2:end),'.gz');
if wantgz
  file0 = file0(1:end-3);  % just end in .nii
end

% ensure directory exists
mkdirquiet(stripfile(file0));

% save NIFTI and gzip it
sz = sizefull(data,3);
if isempty(origin)
  origin = ([1 1 1]+sz)/2;
end
if isempty(tr)
  save_nii(make_nii(data,res,origin),file0);
else
  save_nii(settr_nii(make_nii(data,res,origin),tr),file0);
end
if wantgz
  gzip(file0); delete(file0);
end
