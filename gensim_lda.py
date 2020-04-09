"""
!! This file is not used
"""

import pickle

import re
from gensim import models, corpora
from nltk import word_tokenize
from nltk.corpus import stopwords

# # TODO: Return to active
# This section Creates the corpus using the corpusCreator and taking one section as test
# files, sections = loadCorpus('corpus.pickle')
# section_classified = process_corpus(files)
#
# test_section = section_classified['risk management']
#
data = list()
# for file in test_section:
#     document = ' '.join(file[1])
#     data.append(document.lower())

# TODO: Write normal save/load Function
save = False
if save:
    with open('saved_data/test_risk_management.pickle', 'wb') as pickleWriter:
        pickle.dump(data, pickleWriter)
else:
    with open('saved_data/test_risk_management.pickle', 'rb') as pickleWriter:
        data = pickle.load(pickleWriter)
print('Done!!!')

NUM_TOPICS = 10
STOPWORDS = stopwords.words('english')


def clean_text(text):
    tokenized_text = word_tokenize(text.lower())
    cleaned_text = [t for t in tokenized_text if t not in STOPWORDS and re.match('[a-zA-Z\-][a-zA-Z\-]{2,}', t)]
    return cleaned_text


print('Stating Tokenizing the text ...')
# For gensim we need to tokenize the data and filter out stopwords
tokenized_data = []
for text in data:
    tokenized_data.append(clean_text(text))

print('Building dictionary...')
# Build a Dictionary - association word to numeric id
dictionary = corpora.Dictionary(tokenized_data)

print('Transform the collection of texts to numerical form ...')
# Transform the collection of texts to a numerical form
corpus = [dictionary.doc2bow(text) for text in tokenized_data]

print('Building the LDA model...')
# Build the LDA model
lda_model = models.LdaModel(corpus=corpus, num_topics=NUM_TOPICS, id2word=dictionary)

print("LDA Model:")

for idx in range(NUM_TOPICS):
    # Print the first 10 most representative topics
    print("Topic #%s:" % idx, lda_model.print_topic(idx, 10))