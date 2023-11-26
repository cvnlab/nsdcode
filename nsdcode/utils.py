import numpy as np
from math import floor, ceil

__all__ = ["isnotfinite", "makeimagestack", "zerodiv"]


def isnotfinite(arr):
    """[utility function for finding non-finites]

    Args:
        arr (numpy array): array to find non-finites in

    Returns:
        [bool]: boolean indicating the non-finite elements
    """
    res = np.isfinite(arr)
    np.bitwise_not(res, out=res)  # in-place
    return res


def makeimagestack(m):
    """
    def makeimagestack(m)

    <m> is a 3D matrix.  if more than 3D, we reshape to be 3D.
    we automatically convert to double format for the purposes of this method.
    try to make as square as possible
    (e.g. for 16 images, we would use [4 4]).
    find the minimum possible to fit all the images in.
    """

    bordersize = 1

    # calc
    nrows, ncols, numim = m.shape
    mx = np.nanmax(m.ravel())

    # calculate csize

    rows = floor(np.sqrt(numim))
    cols = ceil(numim/rows)
    csize = [rows, cols]

    # calc
    chunksize = csize[0]*csize[1]

    # total cols and rows for adding border to slices
    tnrows = nrows+bordersize
    tncols = ncols+bordersize

    # make a zero array of chunksize
    # add border
    mchunk = np.zeros((tnrows, tncols, chunksize))
    mchunk[:, :, :numim] = mx
    mchunk[:-1, :-1, :numim] = m

    # combine images

    flatmap = np.zeros((tnrows*rows, tncols*cols))
    ci = 0
    ri = 0
    for plane in range(chunksize):
        flatmap[ri:ri+tnrows, ci:ci+tncols] = mchunk[:, :, plane]
        ri += tnrows
        # if we have filled rows rows, change column
        # and reset r
        if plane != 0 and ri == tnrows*rows:
            ci += tncols
            ri = 0

    return flatmap


def zerodiv(data1, data2, val=0, wantcaution=1):
    """zerodiv(data1,data2,val,wantcaution)
    Args:
        <data1>,<data2> are matrices of the same size or either
                        or both can be scalars.
        <val> (optional) is the value to use when <data2> is 0.
                        default: 0.
        <wantcaution> (optional) is whether to perform special
                        handling of weird cases (see below).
                        default: 1.
        calculate data1./data2 but use <val> when data2 is 0.
        if <wantcaution>, then if the absolute value of one or
                        more elements of data2 is less than 1e-5
                        (but not exactly 0), we issue a warning
                        and then treat these elements as if they
                        are exactly 0.
        if not <wantcaution>, then we do nothing special.

    note some weird cases:
    if either data1 or data2 is [], we return [].
    NaNs in data1 and data2 are handled in the usual way.

    """

    # handle special case of data2 being scalar
    if np.isscalar(data2):
        if data2 == 0:
            f = np.tile(val, data1.shape)
        else:
            if wantcaution and abs(data2) < 1e-5:
                print(
                    'warning: abs value of divisor is less than 1e-5.'
                    'treating the divisor as 0.')
                f = np.tile(val, data1.shape)
            else:
                f = data1/data2

    else:
        # do it
        bad = data2 == 0
        bad2 = abs(data2) < 1e-5
        if wantcaution and np.any(np.logical_and(bad2.ravel(), np.logical_not(bad.ravel()))):
            print(
                'warning: abs value of one or more divisors'
                'less than 1e-5.treating them as 0.')

        if wantcaution:
            data2[bad2] = 1
            f = data1/data2
            f[bad2] = val
        else:
            data2[bad] = 1
            f = data1/data2
            f[bad] = val

    return f
