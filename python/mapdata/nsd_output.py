import os
import numpy as np
import nibabel as nib
import nibabel.freesurfer.mghformat as fsmgh


def nsd_write_vol(data, res, outputfile, origin=None):

    data_class = data.dtype
        
    # create a default header
    header = nib.Nifti1Header()
    header.set_data_dtype(data_class)

    # affine
    affine = np.diag([res]*3 + [1])
    if origin is not None:
        affine[0,-1] = -origin[0]*res
        affine[1,-1] = -origin[1]*res
        affine[2,-1] = -origin[2]*res
    else:
        raise ValueError('i need to specify an origin in the affine.')


    # write the nifti volume
    img = nib.Nifti1Image(data,
                        affine,
                        header)

    img.to_filename(outputfile)

def nsd_write_fs(data, outputfile, fsdir):

        # load template
        # load template
        if (outputfile.find('lh.') != -1):
            hemi='lh'
        elif (outputfile.find('rh.') != -1):
            hemi='rh'
        else:
            raise ValueError('wrong outpufile.')
        
        mgh0 = f'{fsdir}/surf/{hemi}.w-g.pct.mgh'

        img = fsmgh.load(mgh0)
        
        header = img.header
        affine = img.affine

        # Okay, make a new object now...
        v = data[:, np.newaxis].astype(np.float64)
        v_img = fsmgh.MGHImage(v, affine, header=header, extra={})

        v_img.to_filename(outputfile)


