import requests
import stim_analysis as SA
from pprint import pprint
import time
from nltk.stem import snowball

USERNAME = 'mjvolpe'
API_KEY = 'a2cbe279f7e04b809899aace132d173a'
base_url = 'https://api.sketchengine.eu/bonito/run.cgi'

stims = SA.Stims()
raw_words = stims.idioms
Dutch = raw_words[0:30]
English = raw_words[31:60]
German = raw_words[61:90]


# <base_url>/<method>?<attributes_and_values>

class GetWords:

    def __init__(self):
        self.words = [(English, 'English'), (Dutch, 'Dutch'), (German, 'German')]
        self.split_words = {'English': set(), 'Dutch': set(), 'German': set()}
        self.corpora = {'Dutch': 'preloaded/nltenten14_tt3_1', 'English': 'preloaded/ententen15_tt21',
           'German': 'preloaded/detenten13_rft3'}
        self.words_dict = self.make_Set()

    def make_Set(self):
        for language in self.words:
            for idiom in language[0]:
                parts = idiom.split()
                for part in parts:
                    part = part.lower()
                    self.split_words[language[1]].add(part)
            self.split_words[language[1]] = sorted(self.split_words[language[1]])
        return self.split_words


    def query_sketch(self, dictydict):
        frequencies = {'English': {}, 'Dutch': {}, 'German': {}}
        stemmers = {'English': snowball.EnglishStemmer(), 'Dutch': snowball.DutchStemmer(), 'German': snowball.GermanStemmer()}
        for lang in dictydict:
            for lemma in dictydict[lang]:
                with open('noted_frequencies.txt', 'a+') as notebook:
                    data = {
                        'corpname': self.corpora[lang],
                        'format': 'json',
                        'lemma': lemma,
                    }
                    d = requests.get(base_url + '/wordlist?wlattr=lemma;wlpat={};wltype=simple;wlsort=f'.format(data['lemma']), params=data, auth=(USERNAME, API_KEY)).json()
                    pprint(d)
                    try:
                        items = d['Items']
                        freq = items[0]['freq']
                    except IndexError:
                        try:
                            print(
                            '************************Index error!! stemming and retrying...************************')
                            stemmer = stemmers[lang]
                            new_lemma = stemmer.stem(lemma)
                            d = requests.get(base_url + '/wordlist?wlattr=lemma;wlpat={};wltype=simple;wlsort=f'.format(new_lemma), params=data, auth=(USERNAME, API_KEY)).json()
                            pprint(d)
                            items = d['Items']
                            freq = items[0]['freq']
                        except IndexError:
                            print('************************STEMMING FAIL************************')
                            print('{} HAS CAUSED AN ERROR, COULD NOT BE SOLVED BY STEMMING\nCHECK NEW WORD {}'.format(lemma, new_lemma))
                            with open('ERROR_WORDS.txt', 'a+') as f:
                                    f.write('{}'.format(lemma))
                            continue
                        frequencies[lang][lemma] = freq
                    notebook.write('{}, {}\n'.format(lemma, freq))
                    time.sleep(3)
                    # https://app.sketchengine.eu/bonito/run.cgi/wordlist?corpname=preloaded/ententen15_tt21
                    # https://api.sketchengine.eu/bonito/run.cgi/wordlist?corpname=preloaded/bnc2;wlattr=word;wlpat=test.*;wlsort=f;wlmaxitems=2;format=json
                    notebook.close()

               # except
                #    print('index error for item {}! what do?'.format(lemma))
                #    new_lemma = input('What should new lemma be?')
                #    self.words_dict[lang].add(new_lemma)
                #    continue
        return frequencies

    def open_freqs(self, location, language):
        word_freqs = {'Name': language}
        with open(location+'.csv', 'r') as freqs:
            for line in freqs:
                word, value = line.split(',')
                word_freqs[word] = value
        return word_freqs

    def find_freqs(self, location, language):
        frequencies = []
        word_freqs = self.open_freqs(location, language)
        queries = self.words_dict[language]
        for entry in queries:
            try:
                frequencies.append(word_freqs[entry])
            except KeyError:
                print('Error! {} not found'.format(entry))


g = GetWords()
g.query_sketch()