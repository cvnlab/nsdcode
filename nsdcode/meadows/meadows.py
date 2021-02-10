"""[ma_task data utilities]

"""
import os
import glob
import re
import json
import numpy as np
from PIL import Image
from .utils import reorder_rdm


__all__ = [
    "meadows_subjects",
    "load_json_data",
    "get_matask_stim",
    "get_stim_ids",
    "get_matask",
    "get_dragrate"]


def meadows_subjects(subj):
    """[summary]

    Args:
        subj ([type]): [description]

    Returns:
        [type]: [description]
    """

    subjects = {
        'subj01': 'chief-tick',
        'subj02': 'firm-squid',
        'subj03': 'mighty-squid',
        'subj04': 'sacred-hen',
        'subj05': 'sunny-cougar',
        'subj06': 'moved-seal',
        'subj07': 'sure-kiwi',
        'subj08': 'still-toad'
        }

    subject = subjects[subj]

    return subject, subjects


# Load JSON File
def load_json_data(data_dir):
    """[loads the nsd ma_task data_frame]

    Args:
        data_dir ([path]): [path to the dataframe]

    Returns:
        [dict]: [ma task data_frame]
    """
    json_file = os.path.join(
        data_dir,
        'Meadows_nsd-multiple-arrangements_v_v2_tree.json')
    # Read in the meadows json file

    with open(json_file, 'r') as file_data:
        data_store = json.load(file_data)
    # Get the multiple arrangements data

    return data_store


# Get Stimulus ID for Special 100
def get_matask_stim(data_dir='Data'):
    """[return special 100 stimuli]

    Args:
        data_dir ([path]): [where is the data]
        stim_ids [list]: [names of the sorted stimuli]

    Returns:
        images [dict]: dict of stimuli images with key stim_id
                       and value image array
    """
    size = 128, 128
    stim_list = glob.glob(os.path.join(data_dir, 'special100', '*.png'))

    images = {
        re.split(
            '\\\\',
            stim)[2][:-4]: np.asarray(
                Image.open(
                    stim).resize(
                        size=size,
                        resample=Image.BICUBIC)
                        ) for stim in stim_list}
    # Get a dictionary of stimulus images and IDs

    return images


# Get Stimulus ID for a Subject
def get_stim_ids(data_store, subject):
    """[return sorted stim ids]

    Args:
        data_store ([json]): [ma task json data_store]
        subject ([string]): [meadows subject name]

    Returns:
        indcs [list]: [indices for stim sorting]
        stim_ids [list]: [names of the sorted stimuli]
    """

    stimuli = data_store[subject]['tasks'][1]['stimuli']
    # Get the stimulus names from the data_store dictionary

    stim_ids = \
        [int(re.split('nsd', x['name'])[1]) for x in stimuli]
    # Get the 73K ids (used later for reading in the images)
    # Get the nsd integer value from the stimuli variable

    stim_ids_np = np.asarray(stim_ids)
    indcs = np.argsort(stim_ids_np)
    stim_ids = list(stim_ids_np[indcs])
    # Sort the ids (nsa.read_images needs sorted indices)
    # By index sorting then listing using these indexes

    return stim_ids, indcs


def get_matask(data_dir, sub):
    """[fetch the multiple arrangements data]

    Args:
        data_dir ([path]): [where is the data]
        sub ([string]): [subject key]

    Returns:
        [RDM utv]: [upper triangular vector of the RDM]
    """

    this_subject, _ = meadows_subjects(sub)

    data_store = load_json_data(data_dir)
    # Get the data

    stim_ids, indcs = get_stim_ids(data_store, this_subject)
    # Get stim ids and sorting indices

    this_data = data_store[this_subject]['tasks'][1]['rdm']
    # Extract that subject's RDM from the json datastore

    rdm_utv = reorder_rdm(this_data, indcs)
    # Reorder rdm according to sorting indices

    return rdm_utv, stim_ids


def get_dragrate(data_dir, sub, task='valence'):
    """[summary]

    Args:
        data_dir ([type]): [description]
        sub ([type]): [description]
        task (str, optional): [description]. Defaults to 'valence'.

    Returns:
        [type]: [description]
    """

    # Meadows nicknames
    t_sub = meadows_subjects(sub)[0]

    data_store = load_json_data(data_dir)
    # Get the data

    stim_ids, indcs = get_stim_ids(data_store, t_sub)
    # Get stim ids and sorting indices
    # find the dragrate task
    task_is = \
        [i for i, k in enumerate(
            data_store[t_sub]['tasks']
            ) if task in k['task']['name']]

    task_items = []
    for run in task_is[1:]:

        run_items = [[int(
            re.split(
                'nsd',
                pos['name']
                )[1]),
            pos['x'],
            pos['y']
         ] for pos in data_store[t_sub]['tasks'][run]['positions']]

        task_items.append(run_items)

    task_items = np.vstack(task_items)

    reordering = np.argsort(task_items[:, 0])

    scores = task_items[reordering, 2]

    confidence = task_items[reordering, 1]

    stims = task_items[reordering, 0]

    return scores, confidence, stims
