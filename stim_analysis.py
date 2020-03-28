from pprint import pprint
import numpy as np
import scipy.stats as stats
import pandas as pd
import os
import re


class Stims:
    """
    does some basic maths on the lengths of stimuli used in experiment
    """

    def __init__(self, location='./stims'):
        self.location = location
        self.idioms = self.get_idioms()
        self.idioms_len = self.get_idioms_len()
        self.stim_stats = self.get_stats()
        self.dutch = self.idioms_len['dutch']
        self.german = self.idioms_len['german']
        self.english = self.idioms_len['english']

    def get_idioms(self):
        """
        retrieves idioms as text from associated .png files used in experiment
        """
        idioms = []
        for root, dirs, files in os.walk(self.location):
            for file in files:
                if '.PNG' in file or '.png' in file:
                    file, ext = file.split('.')
                    idioms.append(file)
        return idioms

    def write_idioms(self):
        """
        writes idioms to a text file
        """
        with open('../frequencies.txt', 'w') as w:
            idioms = self.get_idioms()
            for item in idioms:
                w.write('{}\n'.format(item))
            w.close()


    def get_idioms_len(self):
        """
        calculates the lengths of each idiom and stores in dictionary
        """
        idioms_len = {'dutch': [], 'english': [], 'german': []}
        block_start = 0
        block_end = 30
        for item in idioms_len:
            # idioms at this point are in a list of 90 items, and each block of 30 corresponds to a language block
            [idioms_len[item].append(len(idiom.split())) for idiom in self.idioms[block_start:block_end]]
            block_end += 30
            block_start += 30
        return idioms_len

    def show_idioms_len(self):
        pprint(self.idioms_len)

    def get_stats(self):
        """
        calculates some rough descriptive statistics
        """
        stats = {}
        for entry in self.idioms_len:
            stats[entry] = ['mean = {}'.format(np.mean(self.idioms_len[entry]))]
            stats[entry].append('std = {}'.format(np.std(self.idioms_len[entry])))
        return stats

    def one_way_anova(self):
        """
        performs a kruskal-wallis test (non-normal data) on idiom lengths
        """
        dutch, german, english = self.dutch, self.german, self.english
        statistic, p_val = stats.f_oneway(dutch, german, english)
        levene = stats.levene(dutch, german, english)
        shapiro = [stats.shapiro(group) for group in [dutch, german, english]]
        kruskal = stats.kruskal(dutch, german, english)
        return print('''F stat = {},\np val = {},\nlevene = {},\nshapiro = {},
        kruskal = {}'''.format(statistic, p_val, levene, shapiro, kruskal))

    def z_score(self):
        """
        calculates Z score of data
        """
        return stats.zscore([np.mean(self.dutch), np.mean(self.english), np.mean(self.german)])

    def word_length(self):
        """
        works out length of each word in stimulus and calculates average for each language
        """
        dutch = self.idioms[0:30]
        english = self.idioms[30:60]
        german = self.idioms[60:90]
        idioms = [(dutch, 'dutch'), (english, 'english'), (german, 'german')]
        for item in idioms:
            avword_lengths = []
            for phrase in item[0]:
                words = phrase.split()
                for unit in words:
                    avword_lengths.append(len(unit) / len(words))
            print(sum(avword_lengths) / 30, item[1])



class SurveyData:
    """
    analysis of experiment results, including demographic data
    """

    def __init__(self, data1='./eng_full_report_Stripped.xlsx',
                 data2='./dut_lang_coded.xlsx', data3='./ger_full_report.xlsx'):
        self.eng_df, self.dut_df, self.ger_df = pd.read_excel(data1), pd.read_excel(data2), pd.read_excel(data3)
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.depths = self.get_languages('./languages.txt')
        self.eng_df = self.outliers(self.language_coder(self.eng_df))
        self.eng_df.name = 'English'
        self.dut_df = self.outliers(self.language_coder(self.dut_df))
        self.dut_df.name = 'Dutch'
        self.ger_df = self.outliers(self.language_coder(self.ger_df))
        self.ger_df.name = 'German'
        self.excel_labeller()
        self.missing_values(self.eng_df)
        self.missing_values(self.dut_df)
        self.missing_values(self.ger_df)
        self.stim_length_labeller()
        self.check_column_difs()
        self.full = self.combiner()
        self.demo = self.drop_times()
        self.reworked = self.make_new_structure()
        self.stats = self.set_stats()

    def excel_labeller(self):
        """
        provides new column in position 0 and fulls that column with a string denoting the language group
        """
        print('adding language group labels...')
        labels = ['English', 'Dutch', 'German']
        frames = [self.eng_df, self.dut_df, self.ger_df]
        for frame in range(len(frames)):
            frames[frame].insert(0, 'Language Group', labels[frame])
        print('language group labels added!')

    def get_languages(self, languages='./languages.txt'):
        """
        retrieves orthographic depth values from .txt file and returns a dictionary
        """
        print('getting language depth coding values...')
        pat_lang = re.compile(r'^([A-Z]\w+\s?\w*)\s/')
        pat_digit = re.compile(r'\.(\d)')
        depths = {}
        with open(languages, 'r') as lang:
            for line in lang:
                lang_match = re.search(pat_lang, line)
                digit_match = re.search(pat_digit, line)
                lang_token = lang_match.group(1)
                digit_token = digit_match.group(1)
                depths[lang_token] = int(digit_token)
        print('language depth coding labels successfully retrieved!')
        return depths

    def language_coder(self, report):
        """
        replaces each given language with its associated depth value
        """
        print('coding languages for depth...')
        depths = self.depths
        for i in range(len(report['Response ID'])):
            for j in range(1, 6):
                try:
                    entry = report.iloc[i, j]
                    entry = entry.strip()
                    if entry in depths.keys():
                        report.iloc[i, j] = depths[entry]
                except AttributeError:
                    pass
        print('languages coded successfully!')
        return report

    def save_coded(self, reports=None, location=None):
        """
        saves newly language-coded dataframes as excel files
        """
        if reports is None:
            reports = [self.eng_df, self.dut_df, self.ger_df]
        if location is None:
            location = ['./eng_report_poked.xlsx', './dut_report_poked.xlsx',
                        './ger_report_poked.xlsx']
        try:
            assert len(reports) == len(location)
            for index in range(len(reports)):
                print('saving {} to {}'.format(reports[index].name, location[index]))
                writer = pd.ExcelWriter(location[index])
                reports[index].to_excel(writer)
                writer.save()
            print('reports successfully saved as xlsx file!')
        except AssertionError:
            print('''save_coded() method takes a list of reports and a list of locations as its arguments. Please ensure
            that you have provided a list of both the same length''')

    def outliers(self, report):
        """
        identifies and removes timing values outside the window of mean +/- 2 * SD
        """
        for column_index in range(-30, 0):
            try:
                col_mean = int(np.mean(report.iloc[:, column_index]))
                col_sd = int(np.std(report.iloc[:, column_index]))
                for row_index in range(len(report['Response ID'])):
                    try:
                        if int(report.iloc[row_index, column_index]) > ((2 * col_sd) + col_mean):
                            print('removing outlying data point:', report.iloc[row_index, column_index])
                            report.iloc[row_index, column_index] = ''
                        elif int(report.iloc[row_index, column_index]) < (col_mean - (2 * col_sd)):
                            print('removing outlying data point:', report.iloc[row_index, column_index])
                            report.iloc[row_index, column_index] = ''
                    except (IndexError, ValueError):
                        pass
            except (IndexError, ValueError):
                pass
        print('all outliers successfully removed!')
        return report

    def missing_values(self, frame):
        """
        fills any omitted values in survey
        """
        print('searching dataframe for missing values and filling appropriately...')
        frame.iloc[:, 8].fillna(value=1.0, inplace=True)
        frame.iloc[:, 13].fillna(value=100.0, inplace=True)
        frame.iloc[:, 14:18].fillna(value=0.0, inplace=True)
        frame.iloc[:, 18].fillna(value=100, inplace=True)
        frame.iloc[:, 19:23].fillna(value=0.0, inplace=True)
        print('NaN and missing values successfully dealt with in dataframe {}!'.format(frame.name))

    def stim_length_labeller(self, frames=None):
        """
        calculates the length of the idiom stimulus and enters that value as int in a new column alongside the
        associated stimulus
        """
        print('labelling stimuli lengths...')
        if frames is None:
            frames = [self.eng_df, self.dut_df, self.ger_df]
        stim_name = re.compile(r'Timing - (.+$)')
        new_names = {}
        for df in frames:
            final_columns = list(df.columns[-30:])
            gen_index = (i for i in range(1, 31))
            for column in final_columns:
                try:
                    stim = str(re.match(stim_name, column).group(1))
                    stim_len = len(stim.split())
                    col_index = list(df.columns).index(column) + 1
                    stim_number = next(gen_index)
                    df.insert(col_index, 'Stim {} length'.format(stim_number), stim_len)
                    new_names[column] = 'Stim {}'.format(stim_number)
                except StopIteration:
                    break
            df.rename(columns=new_names, inplace=True)
        print('stimuli lengths successfully labelled!')

    def check_column_difs(self, frame1=None, frame2=None, frame3=None):
        """
        checks the columns are all the same name to allow rbind in RStudio to work
        """
        if frame1 is None and frame2 is None and frame3 is None:
            frame1, frame2, frame3 = self.eng_df, self.dut_df, self.ger_df
        error_count = 0
        print('checking column discrepencies..')
        for item in range(0, 93):
            try:
                # check pairwise comparisons between column names
                if frame1.columns[item] != frame2.columns[item]:
                    print('{}\n from frame {} DOESNT MATCH\n{} from frame {}'.format(frame1.columns[item],
                                                                                     frame1.iloc[0, 0],
                                                                                     frame2.columns[item],
                                                                                     frame2.iloc[0, 0]))
                    error_count += 1
                if frame2.columns[item] != frame3.columns[item]:
                    print('{}\n from frame {} DOESNT MATCH\n{} from frame {}'.format(frame2.columns[item],
                                                                                     frame2.iloc[0, 0],
                                                                                     frame3.columns[item],
                                                                                     frame3.iloc[0, 0]))
                    error_count += 1
                if frame1.columns[item] != frame3.columns[item]:
                    print('{}\n from frame {} DOESNT MATCH\n{} from frame {}'.format(frame1.columns[item],
                                                                                     frame1.iloc[0, 0],
                                                                                     frame3.columns[item],
                                                                                     frame3.iloc[0, 0]))
                    error_count += 1
            except (AttributeError, IndexError):
                pass
        if error_count == 0:
            print('No discrepencies found!')
        elif error_count > 0:
            print('discrepencies found')

    def combiner(self):
        """
        combines all 3 datasets into one
        """
        full = pd.concat([self.eng_df, self.dut_df, self.ger_df])
        print('all three datasets now combined under attribute self.full')
        return full

    def drop_times(self):
        """
        isolates demographic data from reaction time data
        """
        print('dropping reaction times to keep demography data...')
        cols = self.full.columns[-60:]
        demo = self.full.drop(labels=cols, axis=1, inplace=False)
        print('reaction times successfully dropped!')
        return demo

    # at this point in my analysis I realised I'd need to reformat my data to use in RStudio, as the form created by
    # the above code wasn't correctly formatted for RStudio statistical tests

    def make_new_structure(self):
        """
        reformats existing self.full dataframe into one in which each timing value occupied its own row, with up
        to 30 rows per participant, rather than a single row per participant with multiple columns for each timing value
        """
        print('reworking structure..')
        columns = list(self.demo.columns)
        columns.extend(['Stim length', 'Timing'])
        full = self.full
        reworked = []
        nulls = 0
        for row in range(full.shape[0]):
            times = [(full.iloc[row, -60:-1:2].iloc[i], full.iloc[row, -59::2].iloc[i]) for i in range(30)]
            print('timing data for participant {}'.format(row), times)
            for value in times:
                try:
                    assert np.isnan(value[0]) == False
                    np.sum(value[0])
                    time_stim = pd.Series(value, index=['Timing', 'Stim length'])
                    new_row = self.demo.iloc[row, :].append(time_stim)
                    reworked.append((new_row))
                except (TypeError, AssertionError):
                    nulls += 1
                    pass
        reworked = pd.DataFrame(reworked)
        reworked.name = 'reworked'
        print('{} null values were found and removed'.format(nulls))
        return reworked

    def set_stats(self):
        """
        works out descriptive statistics for timing data by group
        """
        eng = []
        dut = []
        ger = []
        stats = []
        for lang in [('English', eng), ('Dutch', dut), ('German', ger)]:
            for item in range(0, 4267):
                if self.reworked.iloc[item, 0] == lang[0]:
                    lang[1].append(self.reworked.iloc[item, :])
            lang_df = pd.DataFrame(lang[1])
            timing = lang_df.iloc[:, 32]
            ranger = lambda x: np.max(x) - np.min(x)
            statties = '''{} group has mean {},\nSD {},\nand range {}: {} to {},\n lower quartile: {},\nupper 
            quartile: {}\n, median: {}'''.format(lang[0], np.mean(timing), np.std(timing), ranger(timing),
                                                 np.min(timing), np.max(timing), np.percentile(timing, 25),
                                                 np.percentile(timing, 75), np.percentile(timing, 50))
            stats.append(statties)
        return [item for item in stats]

    def get_stats(self):
        return self.stats


SurveyData()
