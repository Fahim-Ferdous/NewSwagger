from pprint import pprint

from nltk import FreqDist
from nltk.tokenize import RegexpTokenizer

from matplotlib import pyplot as plt

from common import stopwords, articles


tokens = []
tokenizer = RegexpTokenizer('''[a-zA-Z0-9-_']+''')

for token in tokenizer.tokenize('\n'.join(articles)):
    token = token.lower()
    if token not in stopwords:
        tokens.append(token)

dist = FreqDist(tokens)

commons = dist.most_common(100)
pprint(commons)
plt.figure(figsize=(19.20, 10.80), dpi=80)
plt.xticks(rotation=60, fontsize=9, ha='right')
plt.subplots_adjust(left=0.042, right=0.992, bottom=0.114, top=0.985)
plt.xlabel('Word')
plt.ylabel('Frequency')

plt.plot(*[[i[0] for i in commons],
           [i[1] for i in commons]])

plt.savefig('wordfreq.png')
