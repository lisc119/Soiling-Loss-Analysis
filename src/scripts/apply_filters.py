#from filter_strings import remove_outlier_strings
#from filter_times import get_sdv_mean_range, get_sdv_mean_range_end, mean_by, time_mask
from datetime import datetime
import pandas as pd
import numpy as np
import copy

from . import filter_strings as fs, filter_times as ft
from .utils import save_data, update_progress

from tqdm.auto import tqdm

default_steps = [
        "Starting filtering",
        "Filter time window",
        "Shift daily aggregated data",
        "Find thresholds",
        "Generate filter masks",
        "Filtering drops",
        "Filtering bad days",
        "Saving data",
        "Finished"
]

def add_temporal(df, drop_extra = True):
    df['TimeOfDay']=df.index
    df['MonthOfYear']=df['TimeOfDay'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%Y-%m'))

    df['H']=df['TimeOfDay'].apply(lambda x: datetime.strftime(datetime.strptime(str(x),'%Y-%m-%d %H:%M:%S'), '%H'))
    if drop_extra:
        df = df.drop(columns= ['MonthOfYear','TimeOfDay']) #change
    df['av_strings']= df.mean(axis=1)
    return df


def optimal_time_window(df, endtime = '23:55'):
    alltimes=df.index.strftime("%H:%M").unique()
    starttimes=alltimes
    endtime = '23:55'
    #
    endtimes= alltimes
    starttime = endtimes[41]
    #
    sdv_starttimes= ft.get_sdv_mean_range(df, starttimes,endtime)
    sdv_endtimes = ft.get_sdv_mean_range_end(df, starttime, endtimes)

    return [sdv_starttimes, sdv_endtimes]


def filter_data(df, window_start = 15, window_end = 19, save_dir = None):

    pbar = tqdm(
            range(len(default_steps)-1),
            desc = "Initializing",
            bar_format = "{desc}: {percentage:.1f}%|{bar}| {n_fmt}/{total_fmt} [Time elapsed: {elapsed} | Time remaining: {remaining}]"
            )

    df = add_temporal(df)
    ########
    pbar.write("Beginning filtering...")
    update_progress(pbar, default_steps, f"Filtering time window ({window_start}-{window_end})...")
    sratio = ft.time_mask(df, str(window_start), str(window_end)) #save this too

    df_D =sratio.resample(rule='D').mean()

    ####Make a fxn for shifting DF time
    update_progress(pbar, default_steps, "Shifting daily aggregated data")
    lagdf_D = pd.DataFrame(copy.deepcopy(df_D))
    for cols in lagdf_D.columns:
        lagdf_D[cols]=lagdf_D[cols]- lagdf_D[cols].shift(1)

    leaddf_D = pd.DataFrame(copy.deepcopy(df_D))
    for cols in leaddf_D.columns:
        leaddf_D[cols]= leaddf_D[cols]-leaddf_D[cols].shift(-1)

    ####Make a fxn for setting threshold
    update_progress(pbar, default_steps, "Finding thresholds...")
    description_dailyagg_lag = lagdf_D.describe()
    mean_lag= description_dailyagg_lag.loc['mean'].mean()
    std_lag= description_dailyagg_lag.loc['std'].mean()

    lower_thresh_lag = mean_lag-std_lag
    upper_thresh_lag = -lower_thresh_lag
    
    description_dailyagg_lead = leaddf_D.describe()
    mean_lead= description_dailyagg_lead.loc['mean'].mean()
    std_lead= description_dailyagg_lead.loc['std'].mean()

    lower_thresh_lead = mean_lag-std_lag
    upper_thresh_lead = -lower_thresh_lag
    ##############################
    #make a boolean fxn
    update_progress(pbar, default_steps, "Generating boolean masks...")
    bool_1=lagdf_D.lt(lower_thresh_lag)
    bool_2 =lagdf_D.gt(upper_thresh_lag)

    bool_3=leaddf_D.lt(lower_thresh_lead)
    bool_4 =leaddf_D.gt(upper_thresh_lead)

    stringmask=bool_1|bool_3
    #didn't use the jump filter stringmask2
    stringmask2=bool_1|bool_2|bool_3|bool_4
    ################################
    update_progress(pbar, default_steps, "Filtering drops...")
    drops_filt_park1 = df_D.mask(stringmask)
    
    drops_filt_park1= drops_filt_park1.drop(columns='av_strings')

    # get boolean for good (True) and bad (False) days
    df_bool_d = ft.bad_day_filter(drops_filt_park1, threshold = 2)

    # mask(substitute) data with NaN for bad days
    update_progress(pbar, default_steps, "Filtering bad days...")
    df_BDfilt_dayfilt_day= drops_filt_park1.mask(df_bool_d)
    # big-drop & bad-day filtered (freq: day)
    
    stringmask= stringmask.drop(columns='av_strings')
    stringmask.head(2)
    df_bool_BDfilt_dayfilt = stringmask & df_bool_d

    # original data (frequency: hour)
    df= df.drop(columns='av_strings')
    df_H = df.resample('H').mean()
    time = [ind for ind in df_H.index if (ind.hour>=16)&(ind.hour<=18)]
    df_H=df_H.loc[time]
    df_bool_h = ft.bad_day_bool_optimized(df_H, df_bool_BDfilt_dayfilt)
    #############

    # mask(substitute) data with NaN for bad days
    df_BDfilt_dayfilt_hour = df_H.mask(df_bool_h) #return this as well
    df_BDfilt_dayfilt_day['mean_PR'] = df_BDfilt_dayfilt_day.loc[:,:].mean(axis=1)
    
    if save_dir is not None:
        update_progress(pbar, default_steps, "Saving dataframes...")
        save_data([sratio, drops_filt_park1, df_BDfilt_dayfilt_hour, df_BDfilt_dayfilt_day],
        ["df_PR_timemasked", "drops_filt","df_BDfilt_dayfilt_hour", "df_BDfilt_dayfilt_day"], save_dir, "filtered")

        save_data([df_bool_d, stringmask, stringmask2, df_bool_BDfilt_dayfilt],
                ["df_bool_d", "stringmask", "stringmask2", "df_bool_BDfilt_dayfilt"],
                save_dir, "masks")

        save_data([description_dailyagg_lag, description_dailyagg_lead, leaddf_D, lagdf_D],
        ["description_dailyagg_lag","description_dailyagg_lead","leaddf_d","lagdf_d"],
        save_dir, "thresholds")
    update_progress(pbar, default_steps, "Done.")
    return [df_BDfilt_dayfilt_hour, df_BDfilt_dayfilt_day]

    #return df
