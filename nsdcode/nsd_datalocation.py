from os.path import join

__all__ = ["nsd_datalocation"]


def nsd_datalocation(base_path, dir0=None):
    """convenience function to find data on your system

    Args:
        dir0 ([str]): 'betas' | 'timeseries' | 'stimuli' | 'behaviour

    Returns: full path to the nsddata directories.

    """
    if dir0 is None:
        f = join(base_path, 'nsddata')
    elif dir0 == 'betas':
        f = join(base_path, 'nsddata_betas')
    elif dir0 == 'timeseries':
        f = join(base_path, 'nsddata_timeseries')
    elif dir0 == 'stimuli':
        f = join(base_path, 'nsddata_stimuli')
    elif dir0 == 'behaviour':
        f = join(base_path, 'nsddata', 'bdata', 'meadows')

    return f
