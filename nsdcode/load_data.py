"""load_transform
"""
import nibabel as nib
import numpy as np


__all__ = ["load_transform","load_sourcedata"]


def load_transform(casenum, tfile):
    """load the transform file

    Args:
        casenum ([type]): [description]
        tfile ([type]): [description]

    Returns:
        [type]: [description]
    """
    # load transform
    if casenum == 1:
        a1_img = nib.load(tfile)
        a1_data = a1_img.get_fdata()  # X x Y x Z x 3
    elif casenum in (2, 3):
        # V x 3 (decimal coordinates) or V x 1 (index)
        a1_img = nib.load(tfile)
        a1_data = a1_img.get_fdata()
        # get rid of extra dims
        a1_data = a1_data.reshape([a1_data.shape[0], -1], order='F')
    elif casenum == 4:
        a1_data = []
        for p in tfile:
            a1_img = nib.load(p)
            a0_data = a1_img.get_fdata()
            a0_data = a0_data.reshape([a0_data.shape[0], -1], order='F')
            # V-across-differentsurfaces x 3 (decimal coordinates)
            a1_data.append(a0_data)
        # now we vertical stack
        a1_data = np.vstack(a1_data)

    return a1_data


def load_sourcedata(casenum, sourcedata):
    """load sourcedata if str filename is passed

    Args:
        casenum (int): data case
        sourcedata ([type]): str or ndarray

    Returns:
        [nd-array]: returns the data array if a str/path is passed

    """
    # load sourcedata
    if isinstance(sourcedata, list):
        sdatatemp = []
        # sourcedata here could already be a list of volumes, or a 
        # list of paths pointing to volumes
        for p in sourcedata:
            if isinstance(p, str):
                temp = nib.load(p).get_fdata()
                temp = temp.reshape([temp.shape[0], -1])
                sdatatemp.append(temp)
                # V-across-differentsurfaces x D
            else:
                sdatatemp.append(p)

            sourcedata = np.vstack(sdatatemp)

    elif isinstance(sourcedata, str):
        if casenum in (1, 2, 3):
            if sourcedata[-4:] == '.mgz':
                source_img = nib.load(sourcedata)
                sourcedata = source_img.get_fdata()
                sourcedata = sourcedata.reshape(
                    [sourcedata.shape[0], -1],
                    order='F')  # squish
            else:
                source_img = nib.load(sourcedata)
                sourcedata = source_img.get_fdata()
                # X x Y x Z x D

    else:
        print('data array passed')

    return sourcedata
