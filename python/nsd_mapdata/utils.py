import numpy as np
from math import floor, ceil

def isnotfinite(arr):
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

    rowstop = rows-1

    # calc
    chunksize = csize[0]*csize[1]
    numchunks = ceil(numim/chunksize)

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


"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
fig, ax = plt.subplots()
im = ax.imshow(flatmap, cmap=cm.coolwarm)
plt.show()
"""
