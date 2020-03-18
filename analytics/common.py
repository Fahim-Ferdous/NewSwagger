from sqlite3 import connect

articles = []
with connect('../NewSwagger/db.sqlite3') as db:
    articles = \
        [i[0] for i in db.execute('select body from articles').fetchall()]

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
