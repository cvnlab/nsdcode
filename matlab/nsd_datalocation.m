function f = nsd_datalocation(dir0)

% function f = nsd_datalocation(dir0)
%
% <dir> (optional) is [] | 'betas' | 'timeseries' | 'stimuli'
%
% Return full path to the nsddata directories.
% Edit this to suit your needs!

if ~exist('dir0','var') || isempty(dir0)
  f = '/home/surly-raid4/kendrick-data/nsd/nsddata/';
else
  switch dir0
  case 'betas'
    f = '/home/surly-raid4/kendrick-data/nsd/nsddata_betas/';
  case 'timeseries'
    f = '/home/surly-raid4/kendrick-data/nsd/nsddata_timeseries/';
  case 'stimuli'
    f = '/home/surly-raid4/kendrick-data/nsd/nsddata_stimuli/';
  end
end
