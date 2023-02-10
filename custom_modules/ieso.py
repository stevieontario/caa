import numpy as np
import pandas as pd
def preprocess_ieso(generic_dataframe):
    '''
    Change IESO Hour 24 to hour 23 and
    hour 1 to hour 00; join Date and Hour
    into type-datetime datehour. So IESO
    Hour 24 which represents data from eleven
    p.m. to midnight is converted to 23:00,
    and represents data from 23 to OO.
    '''
    generic_dataframe.Date = pd.to_datetime(generic_dataframe.Date)
    generic_dataframe.Hour = generic_dataframe.Hour.astype(int)
    generic_dataframe.Hour = generic_dataframe.Hour.values - 1
    generic_dataframe.Hour = generic_dataframe.Hour.astype(str)
    generic_dataframe.Hour = np.array(['0'+i if len(i) < 2 else i for i in generic_dataframe.Hour.values])
    generic_dataframe['Date'] = pd.to_datetime(generic_dataframe.Date) # change to datetime so I can add a day
    generic_dataframe['Date'] = generic_dataframe.Date.dt.strftime('%Y-%m-%d') # change datetime back to string in order to concatenate hour
    generic_dataframe['datehour'] = pd.to_datetime(generic_dataframe.Date.values+' '+generic_dataframe.Hour.values+':00:00',errors='coerce')
    generic_dataframe = generic_dataframe.set_index('datehour')
    del generic_dataframe ['Date']
    del generic_dataframe ['Hour']
    generic_dataframe = generic_dataframe.astype(np.float64) 

    return generic_dataframe

def preprocess_ec(csv):
    tortemps = pd.read_csv(csv)
    tortemps = tortemps.iloc[1:, 4:]
    tortemps = tortemps.set_index('Date/Time (LST)')
    tortemps = tortemps.iloc[:, 4:]
    tortemps.index = pd.to_datetime(tortemps.index)
    tortemps = tortemps.dropna(axis=1, how='all')
    return tortemps

