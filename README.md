# nsdcode
Code related to analyzing the Natural Scenes Dataset

=============================

Code dependencies:

The nsd code has some external dependencies:
  1. The "NIfTI_20140122" toolbox for NIFTI-related functions.
  2. Utilities that come with FreeSurfer ("freesurfer/matlab").
  3. The "ba_interp3" toolbox.
For your convenience, the "external" folder has .zip versions 
of the "NIfTI_20140122" and "ba_interp3" toolboxes.

The cvn code has additional dependencies:
  1. The "cvncode" repository.
  2. The "knkutils" repository.

=============================

General NSD-related examples:

- examples_nsdmapdata.m
  - This document shows several examples of how to use nsd_mapdata.m.

=============================

More specific CVNLAB-related examples:

- examples_anatviz.m
  - This document shows how cvnlookup.m can be used to generate basic surface inspections of anatomical results for the NSD subjects.

- examples_cvnlookup.m
  - This document demonstrates basic usage of cvnlookup.m (which is a wrapper for cvnlookupimages.m).

- examples_cvnlookup2.m
  - This document demonstrates quick-and-dirty usage of cvnlookup.m.

- examples_drawatlasroi.m
  - This document shows the manual drawing of a "nsdgeneral" ROI on the fsaverage surface. This atlas ROI is saved as lh and rh .mgz files to the fsaverage/label directory.

- examples_fullanalysis.m
  - This document demonstrates a simple analysis of the NSD data from start to finish.

- examples_funcviz.m
  - This document shows how cvnlookup.m can be used to generate basic surface inspections of functional results for the NSD subjects.

- examples_surfacetovolume.m
  - This document shows how fsaverage-defined ROIs are converted to individual-subject surface ROIs, and then how those individual-subject surface ROIs are converted to the anat0pt8, func1mm, and func1pt8mm spaces.
