import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit
from sklearn.model_selection import LeaveOneGroupOut, GroupKFold


class Splitter:
    def __init__(self, labels_ind=0, groups_ind=None):
        """
        Initialize object to manage the dataset

        :param labels_ind: index or list of labels.
            If not given, 0 is assumed
        :param groups_ind: index or list of groups.
            If not given, it is assumed that there is no groups
        """
        if isinstance(groups_ind, list):
            raise NotImplementedError("Passing groups directly is not"
                                      "implemented yet.")
        if not isinstance(groups_ind, int):
            raise ValueError("Labels index passing is required")

        self.sep = '\t'
        self.labels_ind = labels_ind
        self.groups_ind = groups_ind
        self.groups = []
        self.main_data = []
        self.artificial = []

    def add_main(self, data):
        """
        Add main dataset, [examples x features]

        :param data:
        """

        self.main_data = data

    def add_artificial(self, artificial):
        """
        Add dataset that is artificially created based on main dataset.
        Group has to be pointed in constructor, and artificial dataset
        has to have identical format as main dataset

        :param path: path to real dataset sentences stored as tsv
        """

        if not self.groups_ind:
            raise RuntimeError("Groups haven't been passed in constructor,"
                               "risk of overfitting.")
        self.artificial.append(artificial)

    def get_data(self):
        """
        :return: Concatenated main and artificial data.
        """
        # appending main data with artificial
        data = self.main_data.copy()
        for artificial in self.artificial:
            data = np.vstack((self.main_data, artificial))
        return data

    @staticmethod
    def print_labels_statistics(labels):
        for unique in np.unique(labels):
            ind = np.where(labels == unique)[0]
            print('Label: ' + unique + ', examples: ' + str(ind.shape[0]))

    def print_statistics(self):
        print("Main dataset")
        labels = self.main_data[:, self.labels_ind]
        self.print_labels_statistics(labels)

        print("Artificial dataset")
        labels = np.array([])
        for artificial in self.artificial:
            labels = artificial[:, self.labels_ind]
        self.print_labels_statistics(labels)

    def stratified_k_fold(self, n_splits=3, shuffle=False, random_state=None):
        """ Stratified k-fold crossvalidation based on sklearn. Split is made
         on main data and artificial data is then added to the train part, but
         artificial data created on the test part of data is ignored.

        :param n_splits: number of splits
        :param shuffle:
        :param random_state:
        :return:
        """
        splits = []
        skf = StratifiedKFold(n_splits=n_splits, shuffle=shuffle,
                              random_state=random_state)

        idx = skf.split(self.main_data, self.main_data[:, self.labels_ind])
        for train_idx, test_idx in idx:

            if self.groups_ind:

                train_idx = self.append_train_idx(test_idx)
                if shuffle:
                    np.random.seed(random_state)
                    np.random.shuffle(train_idx)

            self.self_test(train_idx, test_idx)

            splits.append((train_idx, test_idx))

        return splits

    def split_train_val_test(self, dev_percent=15, test_percent=15,
                             random_state=None):
        """ Standard train-dev-test split based on sklearn. Split is made
         on main data and artificial data is then added to the train part, but
         artificial data created on the test part and development part is
         ignored.
        """
        train_idx = 0
        val_idx = 0
        test_idx = 0

        labels = self.main_data[:, self.labels_ind]

        sss = StratifiedShuffleSplit(test_size=dev_percent+test_percent,
                                     random_state=random_state)

        for train, rest in sss.split(self.main_data, labels):
            percent = test_percent / (dev_percent+test_percent)
            sss2 = StratifiedShuffleSplit(test_size=percent,
                                          random_state=random_state)
            for val, test in sss2.split(self.main_data[rest], labels[rest]):
                train_idx = train
                val_idx = rest[val]
                test_idx = rest[test]
                break
            break

        if self.groups_ind:

            train_idx = self.append_train_idx(np.append(test_idx, val_idx))

            np.random.seed(random_state)
            np.random.shuffle(train_idx)

        self.self_test(train_idx, test_idx)
        self.self_test(train_idx, val_idx)

        return train_idx, val_idx, test_idx

    def append_train_idx(self, test_idx):
        """ Takes train and test indexes of main data and appends
        train_idx to contain artificial data indexes but without examples
        created on test_idx.

        :param test_idx: test indexes of main data
        :return: train indexes of main data and all artificial data without
            tha made based on test_idx examples
        """
        # Find number of indexes
        main_indexes_num = self.main_data.shape[0]
        art_indexes_num = 0

        for artificial in self.artificial:
            art_indexes_num += artificial.shape[0]

        # Append train indexes with all artificial
            train_idx = np.arange(main_indexes_num + art_indexes_num)

        # Find all groups
        groups = self.main_data[:, self.groups_ind]
        for artificial in self.artificial:
            groups = np.hstack((groups, artificial[:, self.groups_ind]))

        # Find groups in test set to delete them from train
        to_remove_groups = groups[test_idx]
        to_remove_indexes = np.array([], dtype=np.int64)
        for group in to_remove_groups:
            to_remove_indexes = np.append(to_remove_indexes,
                                          np.where(groups == group)[0])

        train_idx = np.delete(train_idx, to_remove_indexes)

        return train_idx

    def self_test(self, train_id, test_id):
        """ Check if there is no data leakage between test and train indexes,
        and test and train groups

        :param train_id: Indexes of train set
        :param test_id: Indexes of test set
        :return:
        """
        for tra in train_id:
            for tes in test_id:
                if tra == tes:
                    raise Exception("Data leakage between test and train idx")

        if self.groups_ind:
            groups = self.main_data[:, self.groups_ind]
            for artificial in self.artificial:
                groups = np.hstack((groups, artificial[:, self.groups_ind]))

            gropus_test = groups[test_id]
            gropus_train = groups[train_id]

            for tra in gropus_train:
                for tes in gropus_test:
                    if tra == tes:
                        raise Exception(
                            "Data leakage between test and train groups")