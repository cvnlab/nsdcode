import os
import numpy as np
import nibabel as nib
import nibabel.freesurfer.mghformat as fsmgh
from nsd_datalocation import nsd_datalocation
from nsd_output import nsd_write_vol, nsd_write_fs
from interp_wrapper import interp_wrapper as iw

def nsd_mapdata(subjix,
                sourcespace,
                targetspace,
                sourcedata,
                interptype=None,
                badval=None,
                outputfile=None,
                outputclass=None,
                fsdir=None):
    """nsa_mapdata is used to map functional data between coordinate systems

    Args:
        subjix ([int]):  is the subject number 1-8

        sourcespace (['string']): is a string indicating the source space
                    (where the data currently are)

        targetspace (['string']): is a string indicating target space 
                    (where the data need to go)

        sourcedata ([array or file]):
                    (1) one or more 3D volumes (X x Y x Z x D)
                    (2) a .nii or .nii.gz file with one or more 3D volumes
                    (3) one or more surface vectors (V x D)
                    (4) a .mgz file with one or more surface vectors

        interptype (['string', optional]): interpolation type. options are
                    'nearest' | 'linear' | 'cubic'. Default: 'cubic'.
                    Special cases are 'wta' and 'surfacewta'
                    (more details below).
        badval ([type], optional): is the value to use for invalid locations.
                    Defaults to None.

        outputfile (['string' or None]):
                    (1) a file.nii or file.nii.gz file to write to
                    (2) a [lh,rh].file.mgz file to write to
                    Default is None which means to not write out a file.

        outputclass ([string]): is the output format to use (e.g. 'single').
                    Default is to use the class of <sourcedata>. Note that
                    we always perform calculations in double format and then
                    convert at the end.

        fsdir (['path']):(optional) is the FreeSurfer subject directory for the
                    <targetspace>, like '/path/to/subj%02d' or
                    '/path/to/fsaverage'. We automatically sprintf the <subjix>
                    into <fsdir>. This input is needed only when writing .mgz
                    files.

     There are four types of use-cases:

     (1) volume-to-volume
         This includes [anat* | func* | MNI] -> [anat* | func* | MNI].
         Note that within-space transforms are not implemented
         (e.g. anat1pt0 to anat0pt8), but that is probably not very
         useful anyway.

     (2) volume-to-nativesurface
         This includes:
         [anat* | func* | MNI] -> [white | pial | layerB1 | layerB2 | layerB3].

     (3) nativesurface-to-fsaverage  or  fsaverage-to-nativesurface
         This includes [white] -> [fsaverage] and
                       [fsaverage] -> [white].
         In this case, note that nearest-neighbour
         is always used (<interptype> is ignored).

     (4) nativesurface-to-volume
         This includes [white | pial | layerB1 | layerB2 | layerB3] -> [anat*]
         In this case, a linear weighting scheme is always used, unless you
         specify <interptype> as 'surfacewta' which means to treat each
         dataset as containing discrete integers and perform a winner-take-all
         voting mechanism (this is useful for label data). Also, it is possible
         to supply data defined on multiple surfaces
         (e.g. layerB1 + layerB2 + layerB3) that are collectively mapped to
         volume. To do this, you should supply <sourcespace> as a cell vector
         of strings and supply <sourcedata> as a cell vector of things like
         cases (3) or (4) as described for <sourcedata> (see above). Note that
         it is okay to combine data defined on lh and rh surfaces!

     The valid strings for source and target spaces are:
       'anat0pt5'
       'anat0pt8'
       'anat1pt0'
       'func1pt0'
       'func1pt8'
       'MNI'
       '[lh,rh].white'
       '[lh,rh].pial'
       '[lh,rh].layerB1'
       '[lh,rh].layerB2'
       '[lh,rh].layerB3'
       'fsaverage'

     Map data from one space to another space. The data in the input variable
     <sourcedata> is mapped and returned in the output variable
     <transformeddata>.

     Details on the weighting scheme used for case (4) above:
        Each vertex contributes a linear kernel that has a size
        of exactly 2 x 2 x 2 voxels (at whatever the target
        anatomical resolution is). All of the linear kernels are added
        up, and values are obtained at the center of each volumetric
        voxel. In other words, the value associated with each voxel
        is simply a weighted average of vertices that are near that
        voxel (for example, within +/- 0.8 mm when targeting the
        anat0pt8 space). In the 'surfacewta' case, the integer labeling
        contributing the largest weight wins.

     Details on the 'wta' and 'surfacewta':
       These schemes are winner-take-all schemes. The sourcedata must
       consist of discrete integer labels. Each integer is separately
       mapped as a binary volume using linear interpolation, and the
       integer resulting in the largest value at a given location is
       assigned to that location.
    """

    # setup
    nsd_path = nsd_datalocation()
    tdir = os.path.join(f'{nsd_path}', 'ppdata',
                        f'subj{subjix:02d}', 'transforms')

    # set default interptype
    if interptype is None:
        interptype='cubic'
    
    # set default badval
    if badval is None:
        badval = np.nan

    # figure out what case we are in
    if sourcespace == 'fsaverage' or targetspace == 'fsaverage':
        casenum = 3
    elif targetspace[:3] == 'lh.' or targetspace[:3] == 'rh.':
        casenum = 2
    elif sourcespace[:2] == 'lh.' or sourcespace[:2] == 'rh.':
        casenum = 4
    else:
        casenum = 1

    # deal with basic setup
    if casenum == 1:
        tfile = os.path.join(f'{tdir}',
                             f'{sourcespace}-to-{targetspace}.nii.gz')
    elif casenum == 2 or casenum == 3:
        if targetspace[:3] == 'lh.' or targetspace[:3] == 'rh.':
            hemi = targetspace[:3]
            tfile = os.path.join(f'{tdir}', f'{hemi}{sourcespace}-to-{targetspace[3:]}.mgz')
        else:
            # assert(ismember(sourcespace(1: 3), {'lh.' 'rh.'}))
            hemi = sourcespace[:3]
            tfile = os.path.join(f'{tdir}', f'{hemi}{sourcespace}-to-{targetspace}.mgz')

    elif casenum == 4:
        tfile = []
        for p in sourcespace:
            hemi = p[:3]
            tfile.append(
                os.path.join(f'{tdir}', f'{hemi}.{targetspace}-to-{p[3:]}.mgz'))

    # for writing target volumes, we need to know the voxel size
    if targetspace == 'anat0pt5':
        voxelsize = 0.5
        res = 512
    elif targetspace == 'anat0pt8':
        voxelsize = 0.8
        res = 320
    elif targetspace == 'anat1pt0':
        voxelsize = 1.0
        res = 256
    elif targetspace == 'func1pt0':
        voxelsize = 1.0
    elif targetspace == 'func1pt8':
        voxelsize = 1.8
    elif targetspace == 'MNI':
        voxelsize = 1

    # load transform
    if casenum == 1:
        a1_img = nib.load(tfile)
        a1 = a1_img.get_data()  # X x Y x Z x 3
    elif casenum == 2 or casenum == 3:
        # V x 3 (decimal coordinates) or V x 1 (index)
        a1_img = nib.load(tfile)
        a1 = a1_img.get_data()
        # get rid of extra dims
        a1 = a1.reshape([a1.shape[0], -1], order='F')
    elif casenum == 4:
        a1 = []
        for p in tfile:
            a1_img = nib.load(p)
            a0 = a1_img.get_data()
            a0 = a0.reshape([a0.shape[0], -1], order='F')
            # V-across-differentsurfaces x 3 (decimal coordinates)
            a1.append(a0)
        # now we vertical stack
        a1 = np.vstack(a1)

    # load sourcedata
    if casenum == 1 or casenum == 2 or casenum == 3:
        if sourcedata[-4:] == '.mgz':
            sourcedata = nib.load(sourcedata).get_data()
            sourcedata = sourcedata.reshape([sourcedata.shape[0], -1], order='F') # squish
            # sourcedata = squish(load_mgh(sourcedata),3);              # V x D
        else:
            sourcedata = nib.load(sourcedata).get_data()
            # X x Y x Z x D

    elif casenum == 4:
        sdatatemp = []
        # sourcedata here could already be a list of volumes, or a list
        # path pointing to volumes 
        for p in sourcedata:
            if isinstance(p, str):
                temp = nib.load(p).get_data()
                temp = temp.reshape([temp.shape[0], -1])
                sdatatemp.append(temp)
                # V-across-differentsurfaces x D
            else:
                sdatatemp.append(p)

        sourcedata = np.vstack(sdatatemp)

    sourceclass = sourcedata.dtype

    # deal with outputclass
    if outputclass is None:
        outputclass = sourceclass

    # figure out if we have a 4d nifti as source
    n_dims = sourcedata.ndim

    # do it
    if casenum == 1:    # volume-to-volume
        
        x, y, z, _ = a1.shape
        targetshape = (x, y, z)

        # construct coordinates
        coords = np.c_[a1[:, :, :, 0].ravel(order='F'), 
                       a1[:, :, :, 1].ravel(order='F'), 
                       a1[:, :, :, 2].ravel(order='F')].T(order='F')
        # ensure that 9999 locations will propagate as NaN
        coords[np.where(coords == 9999)] = np.nan
        coords = coords - 1 # coords is based on Kendrick's 1-based indexing.

        if n_dims==4:

            n_images = sourcedata.shape[3]
            transformeddata = []
            for p in range(n_images):
                tmp = iw(sourcedata[:, :, :, p], coords, interptype=interptype).astype(outputclass)
                tmp[np.isnan(tmp)] = badval
                tmp = np.reshape(tmp, targetshape, order='F')
                transformeddata.append(tmp)
        else:

            transformeddata = iw(sourcedata, coords, interptype=interptype).astype(outputclass)
            transformeddata[np.isnan(transformeddata)] = badval
            transformeddata = np.reshape(transformeddata, targetshape, order='F')

        # if user wants a file, write it out
        if outputfile is not None:
            if targetspace == 'MNI':

                outputtype = 'MNI'
                
            else:
                
                outputtype = 'native'

            nsd_write_vol(transformeddata, a1_img, outputfile, outputtype)   
        
    elif casenum==2:    # volume-to-nativesurface

        # construct coordinates
        coords = np.c_[a1[:, 0].ravel(order='F'), 
                       a1[:, 1].ravel(order='F'), 
                       a1[:, 2].ravel(order='F')].T(order='F')
        coords[np.where(coords==9999)] = np.nan  # ensure that 9999 locations will propagate as NaN
        coords = coords - 1 # coords is based on Kendrick's 1-based indexing.


        if n_dims==4:

            n_images = sourcedata.shape[3]
            transformeddata = []
            for p in range(n_images):
                tmp = iw(sourcedata[:, :, :, p], coords, interptype=interptype).astype(outputclass)
                tmp[np.isnan(tmp)] = badval
                transformeddata.append(tmp)

        else:
            transformeddata = iw(sourcedata, coords, interptype=interptype).astype(outputclass)
            transformeddata[np.isnan(transformeddata)] = badval
            

        # if user wants a file, write it out
        if outputfile is not None:
            
            nsd_write_fs(transformeddata, outputfile, fsdir)

            

    elif casenum == 3:    # nativesurface-to-fsaverage  or  fsaverage-to-nativesurface
        
        # use nearest-neighbor and set the output class
        transformeddata = sourcedata[a1,:].astype(outputclass)
  
        # if user wants a file, write it out
        if outputfile is not None:

            nsd_write_fs(transformeddata, outputfile, fsdir)

    elif casenum == 4:
        """
        TODO
        # do stuff
        transformeddata = cast(cvnmapsurfacetovolume_helper(sourcedata.',a1.',res,isequal(interptype,'surfacewta'),badval),outputclass);
        
        # if user wants a file, write it out
        if outputfile is not None:
            
            nsd_write_fs(transformeddata, outputfile, fsdir)
        
        """

    
    return transformeddata
