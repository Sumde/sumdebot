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
            line = line.strip()
            if not line:
                continue

            words = line.split()
            if len(words) <= self.order:
                continue

            self.starts.append(tuple(words[:self.order]))

            for i in range(len(words) - self.order):
                key = tuple(words[i:i+self.order])
                next_word = words[i+self.order]
                self.model[key].append(next_word)

    def generate_from_prompt(self, prompt, max_words=25):
        prompt_words = prompt.split()
        
        key = None
        for i in range(len(prompt_words) - self.order + 1):
            candidate = tuple(prompt_words[i:i+self.order])
            if candidate in self.model:
                key = candidate
                break
        
        if key is None:
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
    
    # def generate(self, max_words=25):
    #     key = random.choice(self.starts)
    #     result = list(key)

    #     for _ in range(max_words - self.order):
    #         next_words = self.model.get(key)
    #         if not next_words:
    #             break
    #         next_word = random.choice(next_words)
    #         result.append(next_word)
    #         key = tuple(result[-self.order:])

    #     return " ".join(result)