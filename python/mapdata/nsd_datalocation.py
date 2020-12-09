from os.path import join


def nsd_datalocation(base_path=None, dir0=None):
    """convenience function to find data on your system

    Args:
        dir0 ([type]): is [] | 'betas' | 'timeseries' | 'stimuli'

    Returns: full path to the nsddata directories.

    Edit this to suit your needs!
    """
    # base_path = join('/home', 'surly-raid4', 'kendrick-data',
    #             'nsd')

    if base_path is None:
        base_path = join(
            '/rds',
            'projects',
            'c',
            'charesti-start',
            'data',
            'NSD'
            )

    if dir0 is None:
        f = join(base_path, 'nsddata')
    elif dir0 == 'betas':
        f = join(base_path, 'nsddata_betas')
    elif dir0 == 'timeseries':
        f = join(base_path, 'nsddata_timeseries')
    elif dir0 == 'stimuli':
        f = join(base_path, 'nsddata_stimuli')

    return f
