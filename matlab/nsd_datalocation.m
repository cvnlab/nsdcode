function f = nsd_datalocation(dir0)

% function f = nsd_datalocation(dir0)
%
% <dir> (optional) is [] | 'betas' | 'timeseries' | 'stimuli'
%
% Return full path to the nsddata directories.
% Edit this to suit your needs!

if ~exist('dir0','var') || isempty(dir0)
  f = '/media/charesti-start/data/NSD/nsddata/';
else
  switch dir0
  case 'betas'
    f = '/media/charesti-start/data/NSD/nsddata_betas/';
  case 'timeseries'
    f = '/media/charesti-start/data/NSD/nsddata_timeseries/';
  case 'stimuli'
    f = '/media/charesti-start/data/NSD/nsddata_stimuli/';
  end
end
