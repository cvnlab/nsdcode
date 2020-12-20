# nsdcode

This repository contains nsd_mapdata.{m,py}, a light-weight utility that
allows the user to map data between different reference spaces
(e.g. anatomical, functional, volume-based, surface-based) in the NSD dataset.
Both MATLAB and Python versions of the utility are provided.

For more information on the NSD dataset, please see http://naturalscenesdataset.org.

For examples of how to use nsd_mapdata, please take a look at examples_nsdmapdata.{m,py}.

Known issues:
* Note that the MATLAB and Python implementations give extremely similar but not
numerically identical results due to differences in interpolation implementation.
Also, voxels near the edges of valid locations are also handled slightly differently
in the Python version.
* The Python version does not yet implement the anat-to-anat case.


## MATLAB

The MATLAB implementation relies on a few external toolboxes that are provided
in the matlab/external directory.

To install, unzip the matlab/external/*.zip files in place, and then

```matlab
addpath(genpath('/path/to/nsdcode/matlab/'));
```

Because the utility relies on transformation files provided with the NSD dataset,
the user must edit **nsd_datalocation.m** with the location of your local copy
of the NSD dataset.


## Python

To install: 

```bash
cd python
python setup.py develop
```

Code dependencies:

There are some external dependencies which are listed in requirements.txt
These are installed automatically when you run the setup above.
These dependencies include:

  1. nibabel
  2. scipy
  3. numpy
  4. tqdm


## Change history

* Version 1.0 (Dec 20, 2020). This is the first official release of the software.
