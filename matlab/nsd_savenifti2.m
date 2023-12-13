function nsd_savenifti2(data,reffile,file0,tr)

% function nsd_savenifti2(data,reffile,file0,tr)
% 
% <data> is X x Y x Z x D (where D >= 1) with volume data
%   for one or more datasets. Can be of a specific format:
%   'int16' or 'single' or 'double'.
% <reffile> is the path to an existing NIFTI file (or can
%   be the output of load_untouch_nii.m on the file)
% <file0> is the path to a .nii.gz (or .nii) file to write.
%   If .gz extension is used, we do the gzip.
% <tr> (optional) is the TR in seconds to set.
%   Default is [] which means do nothing.
%
% Save NIFTI file, inheriting the headers from <reffile>.

% input
if ~exist('tr','var') || isempty(tr)
  tr = [];
end

% deal with file extension
wantgz = isequal(file0(end-2:end),'.gz');
if wantgz
  file0 = file0(1:end-3);  % just end in .nii
end

% ensure directory exists
mkdirquiet(stripfile(file0));

% save NIFTI and gzip it
if ischar(reffile)
  reffile = load_untouch_nii(reffile);
end
reffile.img = data;
switch class(data)
case 'int16'
  reffile.hdr.dime.datatype = 4;
  reffile.hdr.dime.bitpix = 16;
case 'single'
  reffile.hdr.dime.datatype = 16;
  reffile.hdr.dime.bitpix = 32;
case 'double'
  reffile.hdr.dime.datatype = 64;
  reffile.hdr.dime.bitpix = 64;
otherwise
  error;
end
assert(isequal(reffile.hdr.dime.dim(2:4),sizefull(data,3)));
reffile.hdr.dime.dim(5) = size(data,4);  % number of volumes
if size(data,4) > 1
  reffile.hdr.dime.dim(1) = 4;
else
  reffile.hdr.dime.dim(1) = 3;
end
if ~isempty(tr)
  reffile.hdr.dime.pixdim(5) = tr;
end
save_untouch_nii(reffile,file0);
if wantgz
  gzip(file0); delete(file0);
end
