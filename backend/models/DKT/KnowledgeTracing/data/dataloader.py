"""DataLoader helpers for the legacy DKT training pipeline."""

import sys

sys.path.append('../')

import torch.utils.data as torch_data

from Constant import Constants as constants
from data.readdata import DataReader
from data.DKTDataSet import DKTDataSet

DATASET_SPLITS = {
    'assist2009': ('assist2009/builder_train.csv', 'assist2009/builder_test.csv'),
    'assist2015': ('assist2015/assist2015_train.txt', 'assist2015/assist2015_test.txt'),
    'static2011': ('statics2011/static2011_train.txt', 'statics2011/static2011_test.txt'),
    'kddcup2010': ('kddcup2010/kddcup2010_train.txt', 'kddcup2010/kddcup2010_test.txt'),
    'assist2017': ('assist2017/assist2017_train.txt', 'assist2017/assist2017_test.txt'),
    'synthetic': ('synthetic/synthetic_train_v0.txt', 'synthetic/synthetic_test_v0.txt'),
}


def get_train_loader(train_data_path):
    """Build a shuffled training loader from a raw sequence file path."""
    data_reader = DataReader(train_data_path, constants.MAX_STEP, constants.NUM_OF_QUESTIONS)
    train_questions, train_answers = data_reader.getTrainData()
    train_dataset = DKTDataSet(train_questions, train_answers)
    return torch_data.DataLoader(train_dataset, batch_size=constants.BATCH_SIZE, shuffle=True)


def get_test_loader(test_data_path):
    """Build a deterministic evaluation loader from a raw sequence file path."""
    data_reader = DataReader(test_data_path, constants.MAX_STEP, constants.NUM_OF_QUESTIONS)
    test_questions, test_answers = data_reader.getTestData()
    test_dataset = DKTDataSet(test_questions, test_answers)
    return torch_data.DataLoader(test_dataset, batch_size=constants.BATCH_SIZE, shuffle=False)


def get_loader(dataset):
    """Resolve configured dataset names into paired train and test loaders."""
    train_loaders = []
    test_loaders = []
    dataset_paths = DATASET_SPLITS.get(dataset)
    if dataset_paths is None:
        return train_loaders, test_loaders

    train_relative_path, test_relative_path = dataset_paths
    train_loaders.append(get_train_loader(constants.Dpath + f'/{train_relative_path}'))
    test_loaders.append(get_test_loader(constants.Dpath + f'/{test_relative_path}'))
    return train_loaders, test_loaders


LEGACY_EXPORTS = {
    'getTrainLoader': get_train_loader,
    'getTestLoader': get_test_loader,
    'getLoader': get_loader,
}


def __getattr__(name):
    """Expose camelCase loader helpers for untouched legacy training scripts."""
    try:
        return LEGACY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}') from exc
