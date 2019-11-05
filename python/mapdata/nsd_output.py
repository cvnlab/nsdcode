import os
import numpy as np
import nibabel as nib
import nibabel.freesurfer.mghformat as fsmgh

def nsd_write_vol(data, target_img, outputfile, outputtype):

    n_dims = data.ndim

    if n_dims==4:
        # we need to change some vals in the header to write a 4D nifti
        """
        TODO
        """
        pass
    else:        

        if outputtype == 'MNI':
            """ 
            TODO
            # in the case of the target being MNI, we are going to write out LPI NIFTIs.
            # so, we have to flip the first dimension so that the first voxel is indeed
            # Left. also, in ITK-SNAP, the MNI template has world (ITK) coordinates at
            # (0,0,0) which corresponds to voxel coordinates (91,127,73). These voxel
            # coordinates are relative to RPI. So, for the origin of our LPI file that
            # we will write, we need to make sure that we "flip" the first coordinate.
            # The MNI volume has dimensions [182 218 182], so we subtract the first
            # coordinate from 183.
            transformeddata = flipdim(transformeddata,1);  # now, it's in LPI
            origin = [183-91 127 73]
            """
            pass
        
        elif outputtype == 'native':

            img = nib.Nifti1Image(data,
            target_img.affine, target_img.header)

            img.to_filename(outputfile)

def nsd_write_fs(data, outputfile, fsdir):

        # load template
        hemi = outputfile[:2]
        mgh0 = f'{fsdir}/surf/{hemi}.w-g.pct.mgh'

        img = fsmgh.load(mgh0)
        
        header = img.header
        affine = img.affine

        # Okay, make a new object now...
        v = data[:, np.newaxis].astype(np.float64)
        v_img = fsmgh.MGHImage(v, affine, header=header, extra={})

        v_img.to_filename(outputfile)


