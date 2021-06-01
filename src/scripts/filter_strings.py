import pandas as pd
import numpy as np

def detect_outlier_strings(df, outer_var_sd = 1, inner_var_sd = 3):
    
    # Identify outlier strings based on deviation from 1 SD
    mean = df.mean()
    ub = mean.mean() + outer_var_sd*(mean.std())
    lb = mean.mean() - outer_var_sd*(mean.std())

    mean_df = mean.to_frame()
    normal_strings = mean[(mean <= ub) & (mean >= lb)].index.to_list()
    global_outlier_strings = [i for i in mean.index if i not in normal_strings]
    
    # Identify strings with most variability
    sd = df.drop(global_outlier_strings, axis = 1).std()
    ub = sd.mean() + inner_var_sd*(sd.std())
    lb = sd.mean() - inner_var_sd*(sd.std())
    
    sd_df = sd.to_frame()
    normal_strings = sd[(sd <= ub) & (sd >= lb)].index.to_list()
    outlier_strings = global_outlier_strings + [i for i in sd.index if i not in normal_strings]

    return outlier_strings


#### WARNING: this one seems to require a time mask ########
def filter_strings_threshold(dataframe,start_time, end_time, threshold_std=0.01):
    """Filter good performing strings based on flatness of curve (std). Only strings that are performing
    above the median are selected. Uses a midday timewindwo for the analysis"""
    
    time=timemask(dataframe,start_time,end_time)
    
    #calculate the mean and std for each day and string
    df_resampled=dataframe.loc[time].resample('d')
    df_string_mean=df_resampled.mean()
    df_string_std=df_resampled.std()
    
    #calculate the median of all the strings for each day
    df_day_med=df_string_mean.median(axis=1)
    
    ## 1. select flat strings --> strings with small stdv. Returns a boolean mask
    bool_1=df_string_std.lt(threshold_std)
    
    ## 2. select only good performing strings --> strings with mean above median
    bool_2=df_string_mean.gt(df_day_med,axis=0)
    
    ## combine the two boolean masks
    stringmask=bool_1&bool_2
    
    ## return aggregated dataframe and boolean mask
    return stringmask

########
