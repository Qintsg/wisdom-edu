"""Sequence readers for the legacy DKT text dataset format."""

import numpy as np
import itertools
import tqdm


class DataReader:
    """Read raw three-line student records and pad them to a fixed step count."""

    def __init__(self, path, max_step, num_of_questions):
        """Store dataset metadata required for sequence padding and reshaping."""
        # 原始序列文件路径
        self.path = path
        # 每条序列的最大时间步长度
        self.max_step = max_step
        # 题目总数，用于验证编号范围
        self.num_of_questions = num_of_questions

    def _parse_int_sequence(self, sequence_text):
        """Parse one comma-separated line into an int32 numpy sequence."""
        return np.array(sequence_text.strip().strip(',').split(','), dtype=np.int32)

    def _load_split_data(self, split_name):
        """Load one dataset split and pad every sequence to a fixed step count."""
        question_records = np.array([], dtype=np.int32)
        answer_records = np.array([], dtype=np.int32)
        with open(self.path, 'r') as split_file:
            for sequence_length_text, questions_text, answers_text in tqdm.tqdm(
                itertools.zip_longest(*[split_file] * 3),
                desc=f'loading {split_name} data:    ',
                mininterval=2,
            ):
                # 解析原始序列长度，便于计算需要补齐的步数
                sequence_length = int(sequence_length_text.strip().strip(','))
                # 将题号与作答文本转为定长前的整数向量
                questions = self._parse_int_sequence(questions_text)
                answers = self._parse_int_sequence(answers_text)
                # 将序列补齐到 max_step 的整数倍，便于后续 reshape 成批量矩阵
                padding_length = (
                    0
                    if sequence_length % self.max_step == 0
                    else (self.max_step - sequence_length % self.max_step)
                )
                padding_values = np.full(padding_length, -1, dtype=np.int32)
                questions = np.concatenate((questions, padding_values))
                answers = np.concatenate((answers, padding_values))
                # 追加到全局数组，最终会被 reshape 为二维矩阵
                question_records = np.concatenate((question_records, questions))
                answer_records = np.concatenate((answer_records, answers))
        # 每行对应一个固定长度的学生子序列
        return (
            question_records.reshape([-1, self.max_step]),
            answer_records.reshape([-1, self.max_step]),
        )

    def get_train_data(self):
        """Load and pad training records into question and answer matrices."""
        return self._load_split_data('train')

    def get_test_data(self):
        """Load and pad evaluation records into question and answer matrices."""
        return self._load_split_data('test')

    def __getattr__(self, name):
        """Expose legacy camelCase reader methods for untouched DKT scripts."""
        legacy_exports = {
            'getTrainData': self.get_train_data,
            'getTestData': self.get_test_data,
        }
        try:
            return legacy_exports[name]
        except KeyError as exc:
            raise AttributeError(f'{type(self).__name__!r} has no attribute {name!r}') from exc
