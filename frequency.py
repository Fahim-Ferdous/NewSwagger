from pprint import pprint
from sqlite3 import connect

from nltk import FreqDist
from nltk.tokenize import RegexpTokenizer

from matplotlib import pyplot as plt

stopwords = {
        'not', 'has', 'ought', 'but', 'on', 'each', 'at', 'once', 'so',
        "they'd", 'no', 'then', 'doing', 'doesn', "she'd", 'her', 'couldn',
        "who's", 'won', 'having', 'there', 'weren', 'of', "where's", 'with',
        "we'd", 'themselves', 'haven', 'what', 'more', 'after', 'myself',
        "how's", "aren't", 'mustn', 'don', 'being', 'below', 'same', 'd',
        "we're", 'm', 'himself', 'other', 'only', "i've", 'itself', 'some',
        'that', 'shouldn', 'am', "don't", "she's", "wasn't", "hadn't", 'about',
        'his', "that'll", 'the', 'can', 'if', 'up', 're', "you're", 'how',
        'would', 'ain', "should've", 'hasn', 'few', "i'd", 'o', 'yourself',
        'have', "we'll", "she'll", 'during', "isn't", "when's", "shan't",
        "they're", 'from', 'wouldn', "it's", 'were', 'off', 'hadn', 'he',
        'whom', 'a', 'do', 'they', 'very', 'is', 'before', 'wasn', "didn't",
        'll', 'both', 'been', 'should', 'be', 'theirs', 'did', 'why', 'to',
        'over', "there's", 'further', 'who', 'an', 'will', 'ourselves',
        'mightn', 'me', "why's", "mustn't", 'as', 'cannot', 'just', 'ma',
        'by', "you'd", "they've", 'it', 'which', 'under', 'down', "hasn't",
        'its', 'for', 'yourselves', 'him', 'into', 'y', 've', 'needn', 'own',
        'between', 'when', 'nor', "won't", 'this', 'you', 'your', 'above',
        'than', 'hers', 'in', 'my', 'those', 'while', "he'd", "you've",
        'until', "couldn't", 'aren', 'shan', 'didn', 'them', "mightn't",
        "he'll", 'was', 'again', "here's", 'or', 's', "that's", "you'll",
        'could', "we've", 'i', 'herself', 'through', 't', "i'm", 'most', 'all',
        'because', 'ours', 'yours', 'does', 'she', 'we', 'here', 'where',
        'their', "can't", 'too', 'now', 'had', "what's", "he's", "doesn't",
        "let's", 'isn', 'against', 'out', "haven't", "i'll", "weren't",
        "they'll", 'our', 'are', 'any', 'and', 'these', "wouldn't", "needn't",
        'such', "shouldn't", 'also', 'one', 'two', 'last', 'yesterday',
        'tomorrow', 'said'
    }

articles = ''
with connect('db.sqlite3') as db:
    articles = '\n\n'.join(
        [i[0] for i in db.execute('select body from articles').fetchall()])

tokens = []
tokenizer = RegexpTokenizer('''[a-zA-Z0-9-_']+''')

for token in tokenizer.tokenize(articles):
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
