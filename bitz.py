
import pandas as pd


"""simple tool for replacing Dutch terms for levels of schooling with English terms"""
dut = pd.read_excel('../dut_full_report/dut_full_report_Stripped.xlsx')
eng = pd.read_excel('../eng_full_report/eng_full_report_Stripped.xlsx')
education = {'Minder dan middelbare school': 'Less than high school', 'Middlebare school': 'High school', 'Professionele training': 'Professional training'}
education['Een deel van de universiteit'] = 'Some college'
education['Universiteit'] = 'College'
education['Een deel van de graduate school'] = 'Some graduate school'
for i in range(0, 56):
    if dut.iloc[i, 23] in education.keys():
        dut.iloc[i, 23] = education[dut.iloc[i, 23]]

writer = pd.ExcelWriter('../dut_full_report/dut_lang_coded.xlsx')
dut.to_excel(writer)
writer.save()