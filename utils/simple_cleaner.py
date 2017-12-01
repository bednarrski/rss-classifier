import string
from nltk import PorterStemmer
import numpy as np


class SimpleCleaner:
    def __init__(self, stopwords_path):
        self.ps = PorterStemmer()
        with open(stopwords_path) as f:
            self.stopwords = f.read().splitlines()

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def clean_one(self, sentence, lower=True, stop_word=True, to_stem=True,
                  remove_punct=True, token_num=True):
        """ Clean sentence using nltk tools.
        :param sentence: string to clean
        :param lower: lowercase everything
        :param stop_word: delete stopwords
        :param to_stem: stem words
        :param remove_punct: remove punctuation
        :return: cleaned sentence
        """

        if lower:
            tokens = sentence.lower().split()
        else:
            tokens = sentence.split()

        if stop_word:
            tokens = [token for token in tokens if token not in self.stopwords]

        if remove_punct:
            exclude = set(string.punctuation)
            tokens = [token for token in tokens if token not in exclude]
            for i in range(len(tokens)):
                for ex in exclude:
                    tokens[i] = tokens[i].replace(ex, '')

        if token_num:
            for i in range(len(tokens)):
                if self.is_number(tokens[i]):
                    tokens[i] = '_num'

        if to_stem:
            tokens = [self.ps.stem(token) for token in tokens]
        # tokens = [lmt.lemmatize(token) for token in tokens]

        return ' '.join(tokens)
