import re
import numpy as np
from pprint import pprint
import matplotlib.pyplot as plt


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

totals_mil = {'Dutch': [], 'English': [], 'German': []}
for item in stuff.keys():
    for pair in stuff[item]:
        totals_mil[item].append(float(pair[1]))
    pprint(totals_mil[item])

for key in totals_mil.keys():
    print('{}'.format(key))
    print('mean:{}'.format(np.nanmean(totals_mil[key])))
    print('median:{}'.format(np.nanmedian(totals_mil[key])))

plt.plot(totals_mil['Dutch'], color='blue')
plt.plot(totals_mil['English'], color='red')
plt.plot(totals_mil['German'], color='yellow')
plt.show()

