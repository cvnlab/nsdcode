"""transform_data
"""
import numpy as np
from nsdcode.nsd_output import nsd_write_vol, nsd_write_fs
from nsdcode.interp_wrapper import interp_wrapper as iw
from nsdcode.mapsurfacetovolume import mapsurfacetovolume
from tqdm import tqdm


__all__ = ['transform_data']


def transform_data(a1_data, sourcedata, tr_args):
    """transform_data

    Args:
        casenum (int): which case
        a1_data (nd-array): transformation map
        sourcedata (nd-array): data to be interpolated into target space
        tr_args (dict):
            casenum = tr_args['casenum']
            interptype = tr_args['interptype']
            targetspace = tr_args['targetspace']
            voxelsize = tr_args['voxelsize']
            res = tr_args['res']
            outputfile = tr_args['outputfile']
            outputclass = tr_args['outputclass']
            badval = tr_args['badval']
            fsdir = tr_args['fsdir']

    """
    # figure out if we have a 4d nifti as source
    n_dims = sourcedata.ndim

    # do it
    if tr_args['casenum'] == 1:    # volume-to-volume

        xdim, ydim, zdim, _ = a1_data.shape
        targetshape = (xdim, ydim, zdim)

        # construct coordinates
        coords = np.c_[a1_data[:, :, :, 0].ravel(order='F'),
                       a1_data[:, :, :, 1].ravel(order='F'),
                       a1_data[:, :, :, 2].ravel(order='F')].T

        # ensure that 9999 locations will propagate as NaN
        coords[coords == 9999] = np.nan
        coords = coords - 1  # coords is based on Kendrick's 1-based indexing.

        if n_dims == 4:
            # if a stack is passed
            transformeddata = []

            sourcedata = np.moveaxis(sourcedata, -1, 0)

            for sdata in tqdm(sourcedata, desc='volumes'):
                tmp = iw(
                    sdata,
                    coords,
                    interptype=tr_args['interptype']).astype(
                        tr_args['outputclass'])

                tmp[np.isnan(tmp)] = tr_args['badval']
                tmp = np.reshape(tmp, targetshape, order='F')
                transformeddata.append(tmp)

            # reshape as a 4d volume
            transformeddata = np.moveaxis(np.asarray(transformeddata), 0, -1)
        else:

            transformeddata = iw(
                sourcedata,
                coords,
                interptype=tr_args['interptype']).astype(
                    tr_args['outputclass'])

            transformeddata[np.isnan(transformeddata)] = tr_args['badval']
            transformeddata = np.reshape(
                transformeddata,
                targetshape,
                order='F')

        # if user wants a file, write it out
        if tr_args['outputfile'] is not None:
            if tr_args['targetspace'] == 'MNI':
                print('saving image in MNI space')

                transformeddata = np.flip(transformeddata, axis=0)
                origin = np.asarray([183-91, 127, 73]) - 1  # consider -1 here.

            else:
                origin = \
                    (([1, 1, 1] + np.asarray(transformeddata.shape[:3]))/2)-1

            nsd_write_vol(
                transformeddata,
                tr_args['voxelsize'],
                tr_args['outputfile'],
                origin=origin)

    elif tr_args['casenum'] == 2:    # volume-to-nativesurface

        # construct coordinates
        coords = np.c_[a1_data[:, 0].ravel(order='F'),
                       a1_data[:, 1].ravel(order='F'),
                       a1_data[:, 2].ravel(order='F')].T
        # ensure that 9999 locations will propagate as NaN
        coords[coords == 9999] = np.nan
        # coords is based on Kendrick's 1-based indexing.
        coords = coords - 1

        if n_dims == 4:
            transformeddata = []

            sourcedata = np.moveaxis(sourcedata, -1, 0)
            for sdata in tqdm(sourcedata, desc='volumes'):
                tmp = iw(
                    sdata,
                    coords,
                    interptype=tr_args['interptype']).astype(
                        tr_args['outputclass'])

                tmp[np.isnan(tmp)] = tr_args['badval']
                transformeddata.append(tmp)

            # reshape as a n-dim volume
            transformeddata = np.moveaxis(np.asarray(transformeddata), 0, -1)
        else:
            transformeddata = iw(
                sourcedata,
                coords,
                interptype=tr_args['interptype']).astype(
                    tr_args['outputclass'])

            transformeddata[np.isnan(transformeddata)] = tr_args['badval']

        # if user wants a file, write it out
        if tr_args['outputfile'] is not None:

            if tr_args['fsdir'] is None:
                raise ValueError('missing argument: fsdir')

            nsd_write_fs(
                transformeddata,
                tr_args['outputfile'],
                tr_args['fsdir'])

    # nativesurface-to-fsaverage  or  fsaverage-to-nativesurface
    elif tr_args['casenum'] == 3:

        # use nearest-neighbor and set the output class
        if n_dims == 1:
            transformeddata = \
                sourcedata[np.squeeze(a1_data.astype(np.int)) - 1].astype(
                    tr_args['outputclass'])
        elif n_dims > 1:
            transformeddata = \
                sourcedata[np.squeeze(a1_data.astype(np.int)) - 1, :].astype(
                    tr_args['outputclass'])
        # matlab based indexing in a1_data: 0-based in python

        # if user wants a file, write it out
        if tr_args['outputfile'] is not None:

            if tr_args['fsdir'] is None:
                raise ValueError('missing tr dict key: fsdir')

            nsd_write_fs(
                transformeddata,
                tr_args['outputfile'],
                tr_args['fsdir'])

    elif tr_args['casenum'] == 4:
        specialcase = 0
        if tr_args['interptype'] == 'surfacewta':
            specialcase = 1
        transformeddata = mapsurfacetovolume(
            sourcedata.T,
            a1_data.T,
            tr_args['res'],
            specialcase,
            tr_args['badval']
        )

        # reshape as a n-dim volume
        transformeddata = np.moveaxis(np.asarray(transformeddata), 0, -1).squeeze()

        # if user wants a file, write it out
        if tr_args['outputfile'] is not None:
            nsd_write_vol(
                transformeddata,
                tr_args['voxelsize'],
                tr_args['outputfile']
                )

    return transformeddata
