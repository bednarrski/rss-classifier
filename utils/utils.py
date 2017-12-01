import numpy as np


def drop_labels(data, label_idx=0):
    """ Split numpy array into data and labels"""

    labels = data[:, label_idx]
    data = np.delete(data, label_idx, axis=1)

    return data, labels

