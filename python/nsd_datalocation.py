from os.path import join


def nsd_datalocation(dir0=None):
    """[summary]

    Args:
        dir0 ([type]): is [] | 'betas' | 'timeseries' | 'stimuli'

    Returns: full path to the nsddata directories.

    Edit this to suit your needs!
    """

    if dir0 is None:
        f = join('/home', 'surly-raid4',
                 'kendrick-data', 'nsd', 'nsddata')
    elif dir0 == 'betas':
        f = join('/home', 'surly-raid4', 'kendrick-data',
                 'nsd', 'nsddata_betas')
    elif dir0 == 'timeseries':
        f = join('/home', 'surly-raid4', 'kendrick-data',
                 'nsd', 'nsddata_timeseries')
    elif dir0 == 'stimuli':
        f = join('/home', 'surly-raid4', 'kendrick-data',
                 'nsd', 'nsddata_stimuli')

    return f
