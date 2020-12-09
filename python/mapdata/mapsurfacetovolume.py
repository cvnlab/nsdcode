"""mapsurfacetovolume
"""
import numpy as np
from scipy import sparse
from mapdata.utils import zerodiv
from pdb import set_trace

def mapsurfacetovolume(data, vertices, res, specialmode, emptyval):
    """mapsurfacetovolume(data, vertices, res, specialmode, emptyval)

    Args:
        data (nd-array): is the data with dimensionality n_datasets
                         (datasets) x V (vertices).
        vertices (nd-array): is 3 x V with the X-, Y-, and Z- coordinates
                         of the vertices.
        res (int): is the desired volume size. For example, 256 means
                         256 x 256 x 256.
        specialmode (bool): False means usual linear weighting. True
                         means treat each dataset as
            consisting of discrete integer labels and perform a
                         winner-take-all voting mechanism.
        emptyval ([type]): is the value to use when no vertices map
                         to a voxel

    Returns:
        targetdata [nd-array]: the data mapped to a volume in <targetdata>.
    """

    # calc/define
    n_vertices = vertices.shape[1]   # number of vertices
    n_voxels = res**3                # number of voxels
    n_datasets = data.shape[0]                # number of distinct datasets

    # prepare some sparse-related stuff
    vert_range = np.arange(n_vertices)

    # construct X [vertices x voxels,
    # each row has 8 entries with weights, the max for a weight is 3]
    x_old = sparse.coo_matrix((n_vertices, n_voxels))
    for x_n in [-1, 1]:
        for y_n in [-1, 1]:
            for z_n in [-1, 1]:

                # calc the voxel index and the distance
                # away from that voxel index
                if x_n == 1:
                    # ceil-val  (.1 means use weight of .9)
                    x_r = np.ceil(vertices[0, :])
                    x_d = x_r - vertices[0, :]
                else:
                    # val-floor (.1 means use weight of .9)
                    x_r = np.floor(vertices[0, :])
                    x_d = vertices[0, :] - x_r

                if y_n == 1:
                    y_r = np.ceil(vertices[1, :])
                    y_d = y_r - vertices[1, :]
                else:
                    y_r = np.floor(vertices[1, :])
                    y_d = vertices[1, :] - y_r

                if z_n == 1:
                    z_r = np.ceil(vertices[2, :])
                    z_d = z_r - vertices[2, :]
                else:
                    z_r = np.floor(vertices[3, :])
                    z_d = vertices[2, :] - z_r

                # calc # 1 x vertices with the voxel index to go to
                voxel_is = np.ravel_multi_index(
                    (res, res, res),
                    dims=(x_r, y_r, z_r),
                    order='F')
                # 1 x vertices with the weight to assign
                voxel_w = (1 - x_d) + (1 - y_d) + (1 - z_d)

                # construct the entries and add the old one in
                x_new = sparse.coo_matrix(
                    voxel_w,
                    (vert_range, voxel_is),
                    shape=(n_vertices, n_voxels))
                x_new = x_old + x_new
                x_old = x_new

    # do it
    if specialmode == 0:

        # each voxel is assigned a weighted sum of vertex values.
        # this should be done as a weighted average.
        # thus, need to divide by sum of weights.
        # let's compute that now.
        wtssum = np.ones(n_vertices) * x_new   # 1 x voxels

        # take the vertex data and map to voxels
        transformeddata = data * x_new      # n_datasets x voxels

        # do the normalization
        # [if a voxel has no vertex contribution, it gets <emptyval>]
        transformeddata = zerodiv(
            transformeddata,
            np.tile(wtssum, n_datasets),
            emptyval)

        # prepare the results
        transformeddata = np.reshape(
            transformeddata.T,
            [res, res, res, n_datasets],
            order='F')

    else:

        # loop over datasets
        transformeddata = []
        for data_q in np.arange(n_datasets):

            # figure out discrete integer labels
            alllabels = np.union1d(data[data_q, :], []).flatten()
            assert np.all(np.isfinite(alllabels))

            # expand data into separate channels
            # n_voxels x vertices
            datanew = np.zeros(len(alllabels), data.shape[1])
            for c_label in alllabels:
                datanew[c_label, :] = data[data_q, :] == c_label

            # take the vertex data and map to voxels
            mapped = datanew*x_new      # n_voxels x voxels

            # which voxels have no vertex contribution?
            bad = np.sum(mapped, axis=0) == 0

            # perform winner-take-all
            # (mapped is the index relative to alllabels!)
            mapped = np.argmax(mapped, axis=0)

            # figure out the final labeling scheme
            finaldata = alllabels[mapped]

            # put in <emptyval>
            finaldata[bad] = emptyval

            # save
            transformeddata.append(
                np.reshape(
                    finaldata,
                    [res, res, res],
                    order='F')
                )

    return transformeddata
