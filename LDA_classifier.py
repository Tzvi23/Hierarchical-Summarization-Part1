import gensim
import pprint
import os
import pickle
from gensim.utils import simple_preprocess
# NLTK Stop words
from nltk.corpus import stopwords


# Init vars
stop_words = stopwords.words('english')
pp = pprint.PrettyPrinter()
# load vars
# data, id2word, texts, corpus = list(), dict(), list(), list()


def save_pickle(filename, data, gensim_files_dir):
    with open(os.path.join(gensim_files_dir, filename + '.pickle'), 'wb') as data_file:
        pickle.dump(data, data_file)


def load_saved_pickle(filename, gensim_files_dir):
    file_path = filename + '.pickle'
    if not os.path.exists(os.path.join(gensim_files_dir, file_path)):
        return False
    else:
        with open(os.path.join(gensim_files_dir, file_path), 'rb') as data_file:
            return pickle.load(data_file)


def data_status(name, val):
    print(name + ' => {0}'.format(str(val) if not val else 'Data loaded'))


def load_data(model_topics, gensim_files_dir='gensim_files'):  # path to load data if exists):
    gensim_files_dir = os.path.join(gensim_files_dir, model_topics)
    # Check if saved file exisits
    data = load_saved_pickle('data', gensim_files_dir)
    data_status('data', data)
    id2word = load_saved_pickle('id2word', gensim_files_dir)
    data_status('id2word', id2word)
    texts = load_saved_pickle('texts', gensim_files_dir)
    data_status('texts', texts)
    corpus = load_saved_pickle('corpus', gensim_files_dir)
    data_status('corpus', corpus)
    return data, id2word, texts, corpus


def load_data_local(model_topics):  # path to load data if exists):
    global data, id2word, texts, corpus
    # gensim_files_dir = os.path.join(gensim_files_dir, model_topics)
    # Check if saved file exisits
    data = load_saved_pickle('data', model_topics)
    data_status('data', data)
    id2word = load_saved_pickle('id2word', model_topics)
    data_status('id2word', id2word)
    texts = load_saved_pickle('texts', model_topics)
    data_status('texts', texts)
    corpus = load_saved_pickle('corpus', model_topics)
    data_status('corpus', corpus)


def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations


def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]


def load_Model(model_name='gensim_models/10topics/lda_model_trained_10topics.model'):
    pp.pprint('Loading Model')
    return gensim.models.ldamodel.LdaModel.load(model_name)


def load_Model_local(model_name='gensim_models/10topics/lda_model_trained_10topics.model'):
    global current_model
    pp.pprint('Loading Model ' + model_name)
    current_model = gensim.models.ldamodel.LdaModel.load(model_name)


def print_model_topics():
    pp.pprint(current_model.print_topics())


def classify_LDA_model_multiSentence(current_text, current_model):
    result_list = list()
    # Remove dot and new line symbols from the sentences
    current_text = [sent.replace('.\n', '') for sent in current_text]
    local_words = list(sent_to_words(current_text))
    # Remove Stop Words
    local_words_nostops = remove_stopwords(local_words)

    other_corpus = [id2word.doc2bow(text) for text in local_words_nostops]
    for i in range(len(current_text)):
        res = current_model[other_corpus[i]]
        result_list.append(res[0])

    # Returns list of maximum values for each sentence
    final_results_list = list()
    for i in range(len(result_list)):
        final_results_list.append(max(result_list[i], key=lambda item: item[1]))
    return result_list, final_results_list


def classify_LDA_model_oneSentence(current_text, mode='LDA'):
    # current_model = load_Model()
    current_text = current_text.split()
    result_list = list()
    # Remove dot and new line symbols from the sentences
    current_text = [sent.replace('.', '') for sent in current_text]
    # Remove Stop Words
    local_words_nostops = remove_stopwords(current_text)
    local_words_nostops = list(filter(lambda x: len(x), local_words_nostops))

    sent_score = 0

    other_corpus = [id2word.doc2bow(text) for text in local_words_nostops]
    other_corpus = list(filter(lambda x: len(x), other_corpus))  # remove empty lists
    if mode == 'HLDA':
        other_corpus = [item[0] for item in other_corpus]
        result_list = current_model[other_corpus]
        try:
            topic_class, sent_score = max(result_list, key=lambda item: item[1])[0], max(result_list, key=lambda item: item[1])[1]
        except ValueError:
            topic_class = -1
        return topic_class, sent_score
    if mode == 'LDA':
        other_corpus = [item[0] for item in other_corpus]
        result_list = current_model[other_corpus]
        try:
            topic_class, sent_score = max(result_list[0], key=lambda item: item[1])[0], max(result_list[0], key=lambda item: item[1])[1]
        except ValueError:
            topic_class = -1
        return topic_class, sent_score
    else:
        for i in range(len(local_words_nostops)):
            try:  # TODO check how to address the problem "index out of bounds"
                res = current_model[other_corpus[i]]
                result_list.append(res[0])
            except IndexError as e:
                print(e)

    # Returns list of maximum values for each sentence
    final_results_list = list()
    if not any(isinstance(el, list) for el in result_list):  # check if result_list contains inside other lists or just one
        try:
            topic_class = max(result_list, key=lambda item: item[1])[0]
        except ValueError:
            topic_class = -1
    else:
        for i in range(len(result_list)):
            final_results_list.append(max(result_list[i], key=lambda item: item[1]))
        final_results_list_topics = [item[0] for item in final_results_list]
        try:
            topic_class = max(set(final_results_list_topics), key=final_results_list_topics.count)
        except ValueError:
            topic_class = -1
    return topic_class


# data, id2word, texts, corpus = load_data('10Topic')
# current_model = load_Model()

current_model = None
data, id2word, texts, corpus = None, None, None, None
# txt = 'The Company is required by the Companies Act 2006 to include a review of the business and likely future developments.This information is contained in the Chairmans Statement Chief Executives Report and the Finance Review on pages 6 to 15.\n'
#
# X, Y = classify_LDA_model_oneSentence(txt, lda_model)
# print()
