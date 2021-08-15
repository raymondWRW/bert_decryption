import os
import pickle
import random
from collections import Counter
from typing import Dict, List


class DatasetReader:
    def __init__(self, filepath):
        with open(filepath, "r") as f:
            self.text_data = f.read().splitlines()

    def _iterate_word(self):
        for sentence in self.iterate_sentence():
            for word in sentence.split():
                yield word

    def iterate_word(self):
        return self._iterate_word()

    def iterate_sentence(self):
        return iter(self.text_data)


class CryptAlgo:
    def __init__(self,
                 use_dataset_reader: bool = True,
                 dataset_reader: DatasetReader = None,
                 save_pickle_file: str = None):
        if use_dataset_reader:
            assert dataset_reader is not None
            self._init_from_dataset_reader(dataset_reader)
            if save_pickle_file is not None:
                self._save_to_pickle_file(save_pickle_file)
        else:
            assert dataset_reader is None and save_pickle_file is not None
            self._init_from_pickle_file(save_pickle_file)

    def _init_from_dataset_reader(self, dataset_reader):
        raise NotImplementedError

    def _init_from_pickle_file(self, save_pickle_file):
        raise NotImplementedError

    def _save_to_pickle_file(self, save_pickle_file):
        raise NotImplementedError

    def encrypt(self, sentence):
        raise NotImplementedError

    def decrypt(self, sentence):
        raise NotImplementedError


class RandomCode(CryptAlgo):
    NUM_CODE_LENGTH: int = 8
    LOWER_CASE_ALPHABET_SIZE: int = 26
    MAX_VOCAB_SIZE: int = 1000

    def __init__(self,
                 use_dataset_reader: bool = True,
                 dataset_reader: DatasetReader = None,
                 save_pickle_file: str = None):
        # code generation
        self.random_generator = random.Random()
        self.random_generator.seed(42)
        self.characters_choice = [chr(i + ord('a')) for i in range(self.LOWER_CASE_ALPHABET_SIZE)]

        # vocabulary
        self.vocab: Counter = Counter()
        self.vocab_words: List[str] = []
        self.vocab_counts: List[int] = []

        # mapping
        self.map_word_to_code: Dict[str, str] = {}
        self.map_code_to_word: Dict[str, str] = {}

        super().__init__(
            use_dataset_reader=use_dataset_reader,
            dataset_reader=dataset_reader,
            save_pickle_file=save_pickle_file
        )

    def _generate_code(self):
        random_codes = [self.random_generator.randint(0, self.LOWER_CASE_ALPHABET_SIZE - 1) for _ in
                        range(self.NUM_CODE_LENGTH)]
        return "".join([self.characters_choice[i] for i in random_codes])

    def _init_from_dataset_reader(self, dataset_reader):
        for word in dataset_reader.iterate_word():
            self.vocab[word] += 1
        pair_of_words_and_counts = self.vocab.most_common(self.MAX_VOCAB_SIZE)
        self.vocab_words, self.vocab_counts = zip(*pair_of_words_and_counts)
        counter = 0
        codeWords = list(self.vocab_words)
        random.shuffle(codeWords)
        for word in self.vocab_words:
            # while code in self.map_code_to_word:
            #     print("Re-generating code, if this appears very frequently, consider increasing NUM_CODE_LENGTH")
            #     code = self._generate_code()
            self.map_word_to_code[word] = codeWords[counter]
            self.map_code_to_word[codeWords[counter]] = word
            counter += 1

    def _init_from_pickle_file(self, save_pickle_file):
        with open(save_pickle_file, "rb") as f:
            load_dict = pickle.load(f)
        self.vocab = load_dict["vocab"]
        self.vocab_words = load_dict["vocab_words"]
        self.vocab_counts = load_dict["vocab_counts"]
        self.map_word_to_code = load_dict["map_word_to_code"]
        self.map_code_to_word = load_dict["map_code_to_word"]

    def _save_to_pickle_file(self, save_pickle_file):
        save_dict = {
            "vocab": self.vocab,
            "vocab_words": self.vocab_words,
            "vocab_counts": self.vocab_counts,
            "map_word_to_code": self.map_word_to_code,
            "map_code_to_word": self.map_code_to_word,
        }
        with open(save_pickle_file, "wb") as f:
            pickle.dump(save_dict, f)

    def encrypt(self, sentence):
        encrypted_words_list = []
        for word in sentence.split():
            # ignore missing words
            if word not in self.map_word_to_code:
                continue
            encrypted_words_list.append(self.map_word_to_code[word])
        return " ".join(encrypted_words_list)

    def decrypt(self, sentence):
        decrypted_words_list = []
        for code in sentence.split():
            assert code in self.map_code_to_word
            decrypted_words_list.append(self.map_code_to_word[code])
        return " ".join(decrypted_words_list)


if __name__ == '__main__':
    dataset_reader = DatasetReader("test_dataset.txt")
    random_code = RandomCode(
        use_dataset_reader=True,
        dataset_reader=dataset_reader,
        save_pickle_file="random_code.pk"
    )
    sentence = "I went to eat an apple"
    print("Sentence: ", sentence)
    encrypted = random_code.encrypt(sentence)
    print("Encrypted: ", encrypted)
    decrypted = random_code.decrypt(encrypted)
    print("Decrypted: ", decrypted)
    print("Should expect decrypted to be same as sentence")

    print("~" * 88)
    random_code = RandomCode(
        use_dataset_reader=False,
        save_pickle_file="random_code.pk"
    )
    sentence = "I went to eat an apple"
    print("Sentence: ", sentence)
    encrypted = random_code.encrypt(sentence)
    print("Encrypted: ", encrypted)
    decrypted = random_code.decrypt(encrypted)
    print("Decrypted: ", decrypted)
    print("Should be the save as previous output")
