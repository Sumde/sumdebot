import random
import re
from collections import defaultdict

class MarkovBot:
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(list)
        self.starts = []
    
    def train(self, text):
        lines = text.splitlines()
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue

            words = re.findall(r"\b\w+\b", line)
            if len(words) <= self.order:
                continue

            self.starts.append(tuple(words[:self.order]))

            for i in range(len(words) - self.order):
                key = tuple(words[i:i+self.order])
                next_word = words[i+self.order]
                self.model[key].append(next_word)
    
    def generate(self, max_words=25):
        key = random.choice(self.starts)
        result = list(key)

        for _ in range(max_words - self.order):
            next_words = self.model.get(key)
            if not next_words:
                break
            next_word = random.choice(next_words)
            result.append(next_word)
            key = tuple(result[-self.order:])

        return " ".join(result)