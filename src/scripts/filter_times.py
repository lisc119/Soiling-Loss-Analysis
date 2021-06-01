import pandas as pd
import datetime
import copy
import matplotlib.pyplot as plt


def add_temporal(df):
    df['TimeOfDay']=df.index
    df['MonthOfYear']=df['TimeOfDay'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%Y-%m'))

    #df['TimeOfDay']=df['TimeOfDay'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%H:%M:%S'))
    df['H']=df['TimeOfDay'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%H'))
    df = df.drop(columns= ['MonthOfYear','TimeOfDay']) #change
    df['av_strings']= df.mean(axis=1)
    return df


def mean_by(df, time_unit):
    #maskDF = copy.deepcopy(df)
    maskDF = df
    maskDF['fulldate']=df.index
    maskDF.reset_index(inplace=True)
    #create date time column with the time unit format to groupby
    if time_unit=='H':
        maskDF['datetime']=maskDF['fulldate'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H'))
    if time_unit=='d':
        maskDF['datetime']=maskDF['fulldate'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%Y-%m-%d'))
    maskedDF = maskDF.groupby(['datetime']).agg("mean")
    # now have the date time column as index. convert to column and then use for new time_unit column with only the hour or day
    maskedDF['datetime'] = maskedDF.index
    if time_unit=='H':
        maskedDF[time_unit]=maskedDF['datetime'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H'), '%H'))
    if time_unit=='d':
        maskedDF[time_unit]=maskedDF['datetime'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d'), '%d'))
    #use the Date time column as index
    maskedDF.set_index('datetime', drop=True, inplace=True)
    maskedDF[time_unit]= maskedDF[time_unit].apply(lambda x: int(x))   
    return maskedDF


def time_mask(df, start, end):
    #new.set_index('byH', drop=True, inplace=True)
    new =df[(df.H>start)&(df.H< end)]
    new.drop(columns='H', inplace=True)
    return new


##### Lina's code begins #####

def bad_day_bool(df, df_bool):
    df_bool_str = copy.deepcopy(df_bool)
    df_bool_str['date_str'] = df_bool_str.index.map(lambda i: str(i.date()))
    df_bool_str.set_index('date_str', drop = True, inplace = True)
    
    result_data = copy.deepcopy(df)
    for row_name, row in df.iterrows():
        for column_name in row.keys():
            result_data.loc[row_name, column_name] = df_bool_str.loc[str(row_name.date()), column_name]
    return result_data


def bad_day_bool_optimized(df, df_bool):
    return df_bool.resample('h').pad()


# freq of df: day
def bad_day_filter(df, threshold=1):
    '''
    parameter
    ----------
    threshold: value outside 'mean ± threshold * std' will be 'True'.
    '''
    
    anal = pd.Series(df.values.ravel()).describe()
    mean=anal[1]
    std=anal[2]
    
    bool_days_1 = df.lt(mean + (threshold * std))
    bool_days_2 = df.gt(mean - (threshold * std))
    bool_days = bool_days_1 & bool_days_2
    
    return ~bool_days


def timemask(dataframe, start,end):
    time = [ind for ind in dataframe.index if (ind.hour>start)&(ind.hour<end)]
    df_time=dataframe.loc[time]
    return df_time

##### Lina's code ends #####

def filter_days(dataframe, start_time, end_time, threshold=0.006):
    """Filter days with good overall performance based on flatness of curve of the median of 
    all the strings (std). Uses a midday timewindwo for the analysis"""
    
    time=timemask(dataframe,start_time,end_time)
    
    # calculate mean and std for all the strings
    df_mean=dataframe.loc[time].mean(axis=1)
    #df_std=dataframe.std(axis=1)
    
    # calculate mean and std for all the days
    df_resample=df_mean.resample('d')
    df_day_mean=df_resample.mean()
    df_day_std=df_resample.std()

    ## select only flat days --> days with small stdv. Returns a boolean mask
    bool_days=df_day_std.lt(threshold)
    print(f'Dayfilter selected {bool_days.sum()} days')
    
    return bool_days
