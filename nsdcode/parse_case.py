"""parse_case

Returns:
    [int]: which data case we are in.
"""
import os

__all__ = ["parse_case"]


def parse_case(sourcespace, targetspace, tdir):
    """parse_case

    Args:
        sourcespace (string): space in which the source data lies.
        targetspace (string): space to interpolate the source data to.
        tdir (string) : directory where the data lives.

    Returns:
        [int]: which case we are in.
    """
    hemi = None

    # figure out what case we are in
    if isinstance(sourcespace, list):
        casenum = 4
    elif sourcespace == 'fsaverage' or targetspace == 'fsaverage':
        casenum = 3
    elif targetspace[:3] == 'lh.' or targetspace[:3] == 'rh.':
        casenum = 2
    elif sourcespace[:2] == 'lh.' or sourcespace[:2] == 'rh.':
        casenum = 4
    else:
        casenum = 1

    if casenum == 4:
        if not isinstance(sourcespace, list):
            sourcespace = [sourcespace]

    # deal with basic setup
    if casenum == 1:
        tfile = os.path.join(f'{tdir}',
                             f'{sourcespace}-to-{targetspace}.nii.gz')
    elif casenum in (2, 3):
        if targetspace[:3] == 'lh.' or targetspace[:3] == 'rh.':
            hemi = targetspace[:3]
            tfile = os.path.join(
                f'{tdir}',
                f'{hemi}{sourcespace}-to-{targetspace[3:]}.mgz')
        else:
            # assert(ismember(sourcespace(1: 3), {'lh.' 'rh.'}))
            hemi = sourcespace[:3]

            tfile = os.path.join(
                f'{tdir}',
                f'{hemi}{sourcespace[3:]}-to-{targetspace}.mgz'
            )

    elif casenum == 4:
        tfile = []
        for c_space in sourcespace:
            hemi = c_space[:2]
            tfile.append(
                os.path.join(
                    f'{tdir}',
                    f'{hemi}.{targetspace}-to-{c_space[3:]}.mgz'
                )
            )

    return casenum, tfile
