import os
import numpy as np
import nibabel as nib
from nsd_datalocation import nsd_datalocation


def nsd_mapdata(subjix,
                sourcespace,
                targetspace,
                sourcedata,
                interptype='cubic',
                badval=None,
                outputfile=None,
                outputclass=None,
                fsdir=None):
    """nsa_mapdata is used to map functional data between coordinate systems

    Args:
        subjix ([int]):  is the subject number 1-8

        sourcespace (['string']): is a string indicating the source space
                    (where the data currently are)

        targetspace (['string']): is a string indicating the source space
                    (where the data currently are)

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
    tdir = os.path.join('{}'.format(nsd_path), 'ppdata',
                        'subj{:02d}'.format(subjix), 'transforms')

    # figure out what case we are in
    if sourcespace == 'fsaverage' or targetspace == 'fsaverage':
        casenum = 3
    elif targetspace[:3] == 'lh.' or targetspace[:3] == 'lh.':
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
        if targetspace[:2] == 'lh.' or targetspace[:2] == 'rh.':
            hemi = targetspace[:2]
            tfile = f'{tdir}', '{}.{}-to-{}.mgz'.format(
                hemi, sourcespace, targetspace[3:])
        else:
            # assert(ismember(sourcespace(1: 3), {'lh.' 'rh.'}))
            hemi = sourcespace[:2]
            tfile = f'{tdir}', '{}.{}-to-{}.mgz'.format(
                hemi, sourcespace[3:], targetspace)

    elif casenum == 4:
        tfile = []
        for p in sourcespace:
            hemi = p[:2]
            tfile.append(
                f'{tdir}', '{}.{}-to-{}.mgz'.format(hemi, targetspace, p[3:]))

    """
    return transformeddata
    """
