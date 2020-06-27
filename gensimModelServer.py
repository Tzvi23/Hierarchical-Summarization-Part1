#!/usr/bin/env python
# coding: utf-8

# https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/

def build_model(numberOfTopics):
    import re
    import numpy as np
    import pandas as pd
    from pprint import pprint

    # Gensim
    import gensim
    import gensim.corpora as corpora
    from gensim.utils import simple_preprocess
    from gensim.models import CoherenceModel

    # spacy for lemmatization
    import spacy

    import os
    import pickle

    # NLTK Stop words
    from nltk.corpus import stopwords
    stop_words = stopwords.words('english')

    def save_pickle(filename, data, gensim_files_dir):
        with open(os.path.join(gensim_files_dir,  os.path.join(str(numberOfTopics) + 'Topic', filename + '.pickle')), 'wb') as data_file:
            pickle.dump(data, data_file)

    def load_saved_pickle(filename, gensim_files_dir):
        file_path = os.path.join(str(numberOfTopics) + 'Topic', filename + '.pickle')
        if not os.path.exists(os.path.join(gensim_files_dir, file_path)):
            return False
        else:
            with open(os.path.join(gensim_files_dir, file_path), 'rb') as data_file:
                return pickle.load(data_file)

    def data_status(name, val):
        pprint(name + ' => {0}'.format(str(val) if not val else 'Data loaded'))

    gensim_files_dir = 'gensim_files'  # path to load data if exists
    # Check if saved file exisits
    data = load_saved_pickle('data', gensim_files_dir)
    data_status('data', data)
    id2word = load_saved_pickle('id2word', gensim_files_dir)
    data_status('id2word', id2word)
    texts = load_saved_pickle('texts', gensim_files_dir)
    data_status('texts', texts)
    corpus = load_saved_pickle('corpus', gensim_files_dir)
    data_status('corpus', corpus)
    bigram_mod = load_saved_pickle('bigram_mod', gensim_files_dir)
    data_status('bigram_mod', bigram_mod)
    trigram_mod = load_saved_pickle('trigram_mod', gensim_files_dir)
    data_status('trigram_mod', trigram_mod)
    data_words = load_saved_pickle('data_words', gensim_files_dir)
    data_status('data_words', data_words)
    data_words_nostops = load_saved_pickle('data_words_nostops', gensim_files_dir)
    data_status('data_words_nostops', data_words_nostops)
    data_words_bigrams = load_saved_pickle('data_words_bigrams', gensim_files_dir)
    data_status('data_words_bigrams', data_words_bigrams)

    if not os.path.exists(os.path.join('output', 'regex_json_file')):
        print('regex_json_file not exits! Convert corpus to json!\n Cannot build LDA model.')
        exit(1)
    json_data_path = os.path.join('output', 'regex_json_file')  # Load converted corpus to json
    df = pd.read_json(json_data_path)
    df.head()

    if not data:
        # Convert to list
        data = df.content.values.tolist()

        # Remove Emails
        data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]

        # Remove new line characters
        data = [re.sub('\s+', ' ', sent) for sent in data]

        # Remove distracting single quotes
        data = [re.sub("\'", "", sent) for sent in data]

        save_pickle('data', data, gensim_files_dir)
    pprint(data[:1])

    def sent_to_words(sentences):
        for sentence in sentences:
            yield (gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

    if not data_words:
        data_words = list(sent_to_words(data))
        save_pickle('data_words', data_words, gensim_files_dir)
    print(data_words[:1])

    # Build the bigram and trigram models
    if not bigram_mod:
        bigram = gensim.models.Phrases(data_words, min_count=5, threshold=100)  # higher threshold fewer phrases.
    if not trigram_mod:
        trigram = gensim.models.Phrases(bigram[data_words], threshold=100)

    # Faster way to get a sentence clubbed as a trigram/bigram
    if not bigram_mod:
        bigram_mod = gensim.models.phrases.Phraser(bigram)
        save_pickle('bigram_mod', bigram_mod, gensim_files_dir)
    if not trigram_mod:
        trigram_mod = gensim.models.phrases.Phraser(trigram)
        save_pickle('trigram_mod', trigram_mod, gensim_files_dir)
    # See trigram example
    print(trigram_mod[bigram_mod[data_words[0]]])

    # Define functions for stopwords, bigrams, trigrams and lemmatization
    def remove_stopwords(texts):
        return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

    def make_bigrams(texts):
        return [bigram_mod[doc] for doc in texts]

    def make_trigrams(texts):
        return [trigram_mod[bigram_mod[doc]] for doc in texts]

    def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
        """https://spacy.io/api/annotation"""
        texts_out = []
        for sent in texts:
            doc = nlp(" ".join(sent))
            texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
        return texts_out

    if not data_words_nostops:
        # Remove Stop Words
        data_words_nostops = remove_stopwords(data_words)
        save_pickle('data_words_nostops', data_words_nostops, gensim_files_dir)

    if not data_words_bigrams:
        # Form Bigrams
        data_words_bigrams = make_bigrams(data_words_nostops)
        save_pickle('data_words_bigrams', data_words_bigrams, gensim_files_dir)

    if not id2word or not texts:
        # Initialize spacy 'en' model, keeping only tagger component (for efficiency)
        # python3 -m spacy download en
        # To add the package in conda enter in terminal:
        # conda activate <envName>
        # spacy download en
        nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
        nlp.max_length = 1500000
        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])

        print(data_lemmatized[:1])

    if not id2word:
        # Create Dictionary
        id2word = corpora.Dictionary(data_lemmatized)
        save_pickle('id2word', id2word, gensim_files_dir)

    # Create Corpus
    if not texts:
        texts = data_lemmatized
        save_pickle('texts', texts, gensim_files_dir)

    # Term Document Frequency
    if not corpus:
        corpus = [id2word.doc2bow(text) for text in texts]
        save_pickle('corpus', corpus, gensim_files_dir)

    # View
    print(corpus[:1])

    gensim_models_dir = 'gensim_models'

    force_create = True
    # Check if model exists
    if os.path.exists('lda_model_trained.model') and force_create is False:
        pprint('Loading Model')
        lda_model = gensim.models.ldamodel.LdaModel.load('lda_model_trained.model')
    elif force_create is True:
        pprint('Building Model')
        # Build LDA model
        lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                    id2word=id2word,
                                                    num_topics=numberOfTopics,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=100,
                                                    passes=10,
                                                    alpha='auto',
                                                    per_word_topics=True)
        lda_model.save(os.path.join(os.path.join(gensim_models_dir, str(numberOfTopics) + 'topics'), 'lda_model_trained_' + str(numberOfTopics) + 'topics.model'))

    # Print the Keyword in the topics
    pprint(lda_model.print_topics())
    doc_lda = lda_model[corpus]
