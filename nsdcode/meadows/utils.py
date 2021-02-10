import numpy as np
from scipy.spatial.distance import squareform


def reorder_rdm(utv, new_order):
    """[reorder_rdm]

    Args:
        utv ([1D array]): pass an upper-triangular vector
        new_order ([1D array]): condition list order

    Returns:
        [reordered utv]: reordered utv.
    """
    ax, bx = np.ix_(new_order, new_order)
    # Create an open mesh of new_order x new_order
    new_order_rdm = squareform(utv)[ax, bx]
    # Reorganise
    return squareform(new_order_rdm, 'tovector', 0)