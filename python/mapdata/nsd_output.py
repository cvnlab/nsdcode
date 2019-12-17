"""nsd_output
"""
import numpy as np
import nibabel as nib
import nibabel.freesurfer.mghformat as fsmgh


def nsd_write_vol(data, res, outputfile, origin=None):
    """nsd_write_vol writes volumes to disk

    Args:
        data (nd-array): volumetric data to write
        res (float): data acquisition resolution (in mm)
        outputfile (filename/path): where to save
        origin (1d-array, optional): the origin point of the volume.
                                     Defaults to None.

    Raises:
        ValueError: [description]
    """

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
        raise ValueError('i need to have an origin for the affine.')


    # write the nifti volume
    img = nib.Nifti1Image(
        data,
        affine,
        header)

    img.to_filename(outputfile)

def nsd_write_fs(data, outputfile, fsdir):
    """similar to nsd_vrite_vol but for surface mgz

    Args:
        data (nd-array): the surface data
        outputfile (filename/path): where to save
        fsdir (path): we need to know where the fsdir is.

    Raises:
        ValueError: if wrong file name provided, e.g doesn't have
                    lh or rh in filename, error is raised.
    """

    # load template
    # load template
    if outputfile.find('lh.') != -1:
        hemi = 'lh'
    elif outputfile.find('rh.') != -1:
        hemi = 'rh'
    else:
        raise ValueError('wrong outpufile.')

    mgh0 = f'{fsdir}/surf/{hemi}.w-g.pct.mgh'

    img = fsmgh.load(mgh0)

    header = img.header
    affine = img.affine

    # Okay, make a new object now...
    vol_h = data[:, np.newaxis].astype(np.float64)
    v_img = fsmgh.MGHImage(vol_h, affine, header=header, extra={})

    v_img.to_filename(outputfile)
