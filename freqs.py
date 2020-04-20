import re
import numpy as np
from pprint import pprint
import scipy.stats as stats
import copy

Dutch_size = 2253777579
German_size = 16526335416
English_size = 15703895409
corpora_sizes = {'Dutch': Dutch_size, 'German': German_size, 'English': English_size}

pattern = re.compile(r'(\d+),\s([\s\w])*(\d\.\d\d)?/')
stuff = {'Dutch': [], 'English':[], 'German':[]}
with open('./frequencies.txt', 'r') as freqs:
    big_list = []
    for line in freqs:
        try:
            result = re.search(pattern, line)
            raw = result.group(1)
            less = result.group(2)
            per_mil = result.group(3)
            if less is not None:
                per_mil = 0
            big_list.append((raw, per_mil))
        except AttributeError:
            pass
    stuff['Dutch'] = big_list[0:30]
    stuff['English'] = big_list[30:60]
    stuff['German'] = big_list[60:90]


def normaliser(observed, corpus, level=1000000):
    x = observed * level / corpus
    return x


totals_mil = {'Dutch': [], 'English': [], 'German': []}
for item in stuff.keys():
    for pair in stuff[item]:
        totals_mil[item].append(float(pair[1]))


def get_stats(dictionary):
    statistics = []
    for key in dictionary.keys():
        print('{}'.format(key))
        print('mean:{}'.format(np.nanmean(dictionary[key])))
        print('median:{}'.format(np.nanmedian(dictionary[key])))
        print('sd:{}'.format(np.nanstd(dictionary[key])))
        statistics.append([key, np.nanmean(dictionary[key]), np.nanmedian(dictionary[key]), np.nanstd(dictionary[key])])
    print(stats.kruskal(dictionary['Dutch'], dictionary['English'], dictionary['German'], nan_policy='omit'))
    return statistics


#plt.plot(totals_mil['Dutch'], color='blue')
#plt.plot(totals_mil['English'], color='red')
#plt.plot(totals_mil['German'], color='yellow')
#plt.show()


def get_stuff():
    return stuff


def get_totals_mils():
    pprint(totals_mil)


def retrieve_word_freqs(file):
    items_freqs_dict = {'English': {}, 'Dutch': {}, 'German': {}}
    counter = 0
    with open(file, 'r') as f:
        for line in f:
            try:
                if '*' in line:
                    counter += 1
                    continue
                else:
                    line_split = line.split(', ')
                    lang = list(items_freqs_dict.keys())[counter]
                    dict_list = items_freqs_dict[lang]
                    print(line_split[1])
                    dict_list[line_split[0]] = int(line_split[1].strip())
            except (IndexError, ValueError):
                print(line)
                print(line_split)
                break
    items_freqs_list = copy.deepcopy(items_freqs_dict)
    for item in items_freqs_dict:
        items_freqs_list[item] = [normaliser(number, corpora_sizes[item]) for number in items_freqs_dict[item].values()]
    return items_freqs_dict, items_freqs_list


freq_dict, freq_list = retrieve_word_freqs('noted_frequencies.txt')
get_stats(freq_list)
get_stats(get_stuff())
