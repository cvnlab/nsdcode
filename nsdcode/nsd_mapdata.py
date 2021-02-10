"""nsd_mapdata
"""
import os
from nsdcode.nsd_datalocation import nsd_datalocation
from nsdcode.parse_case import parse_case
from nsdcode.load_data import load_transform, load_sourcedata
from nsdcode.transform_data import transform_data

__all__ = ["NSDmapdata"]


class NSDmapdata():

    def __init__(self, base_dir):
        """[summary]

        Args:
            base_dir ([os.path]): directory where the nsd_data lives
        """
        self.base_dir = base_dir

    def fit(self,
            subjix,
            sourcespace,
            targetspace,
            sourcedata,
            interptype=None,
            badval=None,
            outputfile=None,
            outputclass=None,
            fsdir=None,
            ):
        """nsa_mapdata is used to map functional data between coordinate systems

        Arguments:
        __________

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

        Returns:
        ________

        transformeddata: [array] data mapped to targetspace.


        There are four types of use-cases:

        (1) volume-to-volume:
        _____________________


        This includes [anat* | func* | MNI] -> [anat* | func* | MNI].
        Note that within-space transforms are not implemented
        (e.g. anat1pt0 to anat0pt8), but that is probably not very
        useful anyway.

        (2) volume-to-nativesurface:
        ____________________________


        This includes:

        [anat* | func* | MNI] -> [white | pial | layerB1 | layerB2 | layerB3].

        (3) nativesurface-to-fsaverage  or  fsaverage-to-nativesurface:
        _______________________________________________________________


        This includes [white] -> [fsaverage] and
                    [fsaverage] -> [white].
        In this case, note that nearest-neighbour
        is always used (<interptype> is ignored).

        (4) nativesurface-to-volume:
        ____________________________

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

        Map data from one space to another space. The data in the input
        variable <sourcedata> is mapped and returned in the output variable
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

        In the case of the target being MNI, we are going to write out LPI
        NIFTIs.
        so, we have to flip the first dimension so that the first voxel is
        indeed Left. also, in ITK-SNAP, the MNI template has world (ITK)
        coordinates at (0,0,0) which corresponds to voxel coordinates
        (91,127,73). These voxel coordinates are relative to RPI. So, for the
        origin of our LPI file that we will write, we need to make sure that we
        "flip" the first coordinate. The MNI volume has dimensions
        [182 218 182], so we subtract the first coordinate from 183.
        transformeddata = flipdim(transformeddata,1);  # now, it's in LPI
        origin = [183-91 127 73]

        """

        # setup
        nsd_path = nsd_datalocation(self.base_dir)
        tdir = os.path.join(f'{nsd_path}', 'ppdata',
                            f'subj{subjix:02d}', 'transforms')

        # set default interptype
        if interptype is None:
            interptype = 'cubic'

        # set default badval
        if badval is None:
            badval = 0

        # figure out which case
        casenum, tfile = parse_case(sourcespace, targetspace, tdir)

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
            res = None
        elif targetspace == 'func1pt8':
            voxelsize = 1.8
            res = None
        elif targetspace == 'MNI':
            voxelsize = 1
            res = None
        else:
            voxelsize = None
            res = None

        # load transform
        a1_data = load_transform(casenum, tfile)

        # load sourcedata
        sourcedata = load_sourcedata(casenum, sourcedata)

        sourceclass = sourcedata.dtype

        # deal with outputclass
        if outputclass is None:
            outputclass = sourceclass

        # collect arguments for transform_data
        transform_args = {
            'casenum': casenum,
            'sourcespace': sourcespace,
            'targetspace': targetspace,
            'interptype': interptype,
            'badval': badval,
            'outputfile': outputfile,
            'outputclass': outputclass,
            'voxelsize': voxelsize,
            'res': res,
            'fsdir': fsdir}

        # apply transform
        transformeddata = transform_data(
            a1_data,
            sourcedata,
            transform_args)

        return transformeddata
