"""interp_wrapper
"""
import numpy as np
from scipy.ndimage import map_coordinates
from nsdcode.utils import isnotfinite

__all__ = ["interp_wrapper"]


def interp_wrapper(vol, coords, interptype='cubic'):
    """
     interp_wrapper(vol, coords, interptype)

     <vol> is a 3D matrix (can be complex-valued)
     <coords> is 3 x N with the matrix coordinates to interpolate at.
       one or more of the entries can be NaN.
     <interptype> (optional) is 'nearest' | 'linear' | 'cubic' | 'wta'.  
        default: 'cubic'.

     this is a convenient wrapper for ba_interp3.  the main problem with
     normal calls to ba_interp3 is that it assigns values to interpolation
     points that lie outside the original data range.  what we do is to
     ensure that coordinates that are outside the original field-of-view
     (i.e. if the value along a dimension is less than 1 or greater than
     the number of voxels in the original volume along that dimension)
     are returned as NaN and coordinates that have any NaNs are returned
     as NaN.

     another feature is 'wta' (winner-take-all). this involves the assumption
     that <vol> contains only discrete integers. each distinct integer is
     mapped as a binary volume (0s and 1s) using linear interpolation to each
     coordinate, the integer with the largest resulting value at that
     coordinate wins, and that coordinate is assigned the winning integer.

     for complex-valued data, we separately interpolate the real and imaginary
     parts.

     history:
     2019/09/01 - ported to python by ian charest

    """
    # input
    if interptype == 'cubic':
        order = 3
    elif interptype == 'linear':
        order = 1
    elif interptype == 'nearest':
        order = 0
    elif interptype == 'wta':
        order = 1  # linear
    else:
        raise ValueError('interpolation method not implemented.')

    # convert vol to float (needed)
    # vol = vol.astype(np.float32)

    # bad locations must get set to NaN
    bad = np.any(isnotfinite(coords), axis=0)
    coords[:, bad] = 1

    # out of range must become NaN, too
    bad = np.any(
        np.c_[
            bad,
            coords[0, :] < 1,
            coords[0, :] > vol.shape[0],
            coords[1, :] < 1,
            coords[1, :] > vol.shape[1],
            coords[2, :] < 1,
            coords[2, :] > vol.shape[2]], axis=1).astype(bool)

    # resample the volume
    if not np.any(np.isreal(vol)):
        # we interpolate the real and imaginary parts independently
        transformeddata = map_coordinates(
            np.nan_to_num(np.real(vol)).astype(np.float64),
            coords,
            order=order,
            mode='nearest') + 1j*map_coordinates(
                np.nan_to_num(np.imag(vol)).astype(np.float64),
                coords,
                order=order,
                mode='nearest')

    else:
        # this is the tricky 'wta' case
        if interptype == 'wta':

            # figure out the discrete integer labels
            alllabels = np.unique(vol.ravel())
            assert np.all(np.isfinite(alllabels))
            if len(alllabels) > 1000:
                print('warning: more than 1000 labels are present')

            # loop over each label
            allvols = []
            for c_label in alllabels:
                allvols.append(map_coordinates(
                    np.nan_to_num(vol == c_label).astype(np.float64),
                    coords,
                    order=order,
                    mode='nearest'
                    ))

            # make into a numpuy stack
            allvols = np.vstack(allvols)

            # which coordinates have no label contribution?
            realbad = np.sum(allvols, axis=0) == 0

            # perform winner-take-all (wta_is is the
            # index relative to alllabels!)
            wta_is = np.argmax(allvols, axis=0)

            # figure out the final labeling scheme
            transformeddata = alllabels[wta_is]

            # fill in NaNs for coordinates with no label
            # contribution and bad coordinates too
            transformeddata[realbad] = np.nan
            transformeddata[bad] = np.nan

        # this is the usual easy case
        else:
            # consider using mode constant with a cval.
            transformeddata = map_coordinates(
                np.nan_to_num(vol).astype(np.float64),
                coords,
                order=order,
                mode='nearest'
            )
            transformeddata[bad] = np.nan

    return transformeddata
