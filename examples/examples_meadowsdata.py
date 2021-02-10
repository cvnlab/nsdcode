import os
import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr
from mapdata.nsd_datalocation import nsd_datalocation
from meadows.meadows import (get_matask,
                             get_dragrate,
                             load_json_data,
                             meadows_subjects)

# establish where the behavioural data is in the data directories
base_path = os.path.join('/media', 'charesti-start', 'data', 'NSD')
data_dir = nsd_datalocation(base_path=base_path, dir0='behaviour')

# let's get the final RDM from the multiple arrangements task
rdm, stims = get_matask(data_dir, 'subj01')

# let's get the dragrate data for 'arousal'
arousal, a_conf, a_stims = get_dragrate(data_dir, 'subj01', task='arousal')

# let's limit to the special 100
arousal_100 = np.asarray(
    [arousal[i] for i, stim in enumerate(a_stims) if stim in stims])

# let's get the dragrate data for 'valence'
valence, v_conf, v_stims = get_dragrate(data_dir, 'subj01', task='valence')

valence_100 = np.asarray(
    [valence[i] for i, stim in enumerate(v_stims) if stim in stims])

# let's make a quick affective model
# here we assume that affect is summarised by a 2-dimensional
# space (arousal and valence) and each stimulus is a point in this space.
# to measure the distance between pairs stimuli, for each pair, we simply
# measure the euclidean distance between the coordinates of the 2 items
# in the pair.

affect = np.c_[arousal_100, valence_100]

affect_rdm = pdist(affect, metric='euclidean')

# is the MA and affect correlated?
rel = spearmanr(rdm, affect_rdm)

# ok now let's see what else in the json
data = load_json_data(data_dir)

subj_key = meadows_subjects('subj01')[0]

for k in data[subj_key]['tasks']:
    print(k['task'])

# the submodules demoed above show you how to easily access
# the task data.
