from os.path import join


def nsd_datalocation(dir0=None):
    """convenience function to find data on your system

    Args:
        dir0 ([type]): is [] | 'betas' | 'timeseries' | 'stimuli'

    Returns: full path to the nsddata directories.

    Edit this to suit your needs!
    """
    # base_path = join('/home', 'surly-raid4', 'kendrick-data',
    #             'nsd')

    base_path = join('/media', 'charesti-start','data','NSD')             

    if dir0 is None:
        f = join(base_path, 'nsddata')
    elif dir0 == 'betas':
        f = join(base_path, 'nsddata_betas')
    elif dir0 == 'timeseries':
        f = join(base_path, 'nsddata_timeseries')
    elif dir0 == 'stimuli':
        f = join(base_path, 'nsddata_stimuli')

    return f
