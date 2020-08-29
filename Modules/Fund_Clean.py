import pandas as pd
from datetime import date
import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

pd.reset_option('display.float_format')



def pconvert(x):
    x = str(x).replace('%','')
    x = str(x).replace(',','')
    return x


def convert(string):
    
    try:
        #try a mathematical calculation to check if already a number
        # if it is simply return value
        int(64) * int(string)
        return(float(string))
    
    except:
               
        #find parenthetical, B, or M indicators
        regex = re.compile(r'[\( \)]')
        p = ''.join(regex.findall(string))

        regex = re.compile(r'B')
        b = ''.join(regex.findall(string))

        regex = re.compile(r'M')
        m = ''.join(regex.findall(string))

        #negative if enclosed in parenthetical
        if p == '()':
            neg = -1
        else:
            neg = 1

        #Billions if ends in B
        if b == 'B':
            mult = 1000000

        #Millions if ends in B
        elif m == 'M':
            mult = 1000
        else:
            mult = 1

        #pull out the number
        regex = re.compile(r'\d+(\..*)?\d')
        value = regex.search(string)

        #convert to integer
        try:
            value = float(value.group())
        except:
            value = 0

        #multiply by negative flag and multiple established above
        return round(float(value) * neg * mult,2)


def DataConversions(data):
    data.epsgrowth = data.epsgrowth.apply(pconvert).astype(float)
    data.roa = data.roa.apply(pconvert).astype(float)
    data.eps = data.eps.apply(convert).astype(float)
    data.netincome = data.netincome.apply(convert).astype('int64')
    data.shareholderequity = data.shareholderequity.apply(convert).astype('int64')
    data.longtermdebt = data.longtermdebt.apply(convert).astype('int64')
    data.interestexpense = data.interestexpense.apply(convert).astype('int64')
    data.ebitda = data.ebitda.apply(convert).astype('int64')
    data['ST Debt'] = data['ST Debt'].apply(convert).astype('int64')
    data.Cash = data.Cash.apply(convert).astype('int64')
    data = data[data.Cash>0] #remove companies with no cash
    data['TotalDebt'] = data.longtermdebt + data['ST Debt']
    data['D2C'] = data.TotalDebt / data.Cash
    data['ROE'] = data.netincome/data.shareholderequity
    data['Sales'] = data.Sales.apply(convert).astype(float)
    data['Shares'] = data.Shares.apply(convert).astype(float)


def CleanFund(companies, df, dfQ):
    
    df = pd.read_csv(filenameA, index_col = 0) #YE2019 
    dfQ = pd.read_csv(filenameQ, index_col = 0) #MRQ

    df = df.replace('-', 0).reset_index()
    dfQ = dfQ.replace('-', 0).reset_index()
    #Get List of S&P
    os.chdir(companylistpath)
    companies = pd.read_csv(companylist,encoding= 'unicode_escape')
    Symbol = companies.Symbol
    companies.columns = ['Ticker', 'Name', 'Sector']
    
    
    
    # convert the text to numbers based on my functions
    import warnings
    warnings.filterwarnings('ignore')
    df = DataConversions(df)
    dfQ = DataConversions(dfQ)

    #create a dataframe for the trailing 12 month eps
    dfQ = dfQ[dfQ['index'] != 'MRQ-4'].sort_values(by = 'Ticker')
    epsQ = dfQ.loc[:,('Ticker','eps')]
    epsQ.columns = ['Ticker', 'epsTTM']
    epsQ = epsQ.groupby('Ticker').sum()

    #create a dataframe for the most recent quarter's Debt to Cash Ratio
    MRQ_D2C = dfQ[dfQ['index'] == 'MRQ'].loc[:,('Ticker','D2C', 'TotalDebt', 'epsgrowth')]
    MRQ_D2C.columns = ['Ticker', 'MRQ_D2C', 'MRQ_TotalDebt', 'MRQ_epsGrowth']

    new = pd.merge(df,epsQ, on ='Ticker', how = 'left')
    new = pd.merge(new,MRQ_D2C, on = 'Ticker', how = 'left' )
    new = pd.merge(new, companies, on = 'Ticker')
    
    return new