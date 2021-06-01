import rdtools
from rdtools.soiling import soiling_srr
import matplotlib.pyplot as plt
import numpy as np
import pathlib

###########
# Suppress RunTimeWarnings of experimental module:

import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

###########
### read env data
def prep_data(df1, df1_env):
    dataframes=[df1,df1_env]
    for df in dataframes:
        df.datetime = df.datetime.apply(lambda x: pd.to_datetime(x,format='%Y-%m-%d %H:%M:%S'))

    df1_env.rename(columns={'Temp_Amb_celsius':'Temp_A','Temp_Panel_celsius': 'Temp_P','Irradiance_kWm2':'Irradiance'},inplace=True)

    df1_env['datetime'] = pd.to_datetime(df1_env['datetime'], format='%Y-%m-%d %H')
    df1_env.set_index('datetime', drop = True, inplace = True)
    return [df1, df1_env]
######

#######
def estimate_soiling(df_BDfilt_dayfilt_daily_mean_series, df1_env):
    daily_irr = df1_env['Irradiance'].resample('D').sum()
    ########################
    # Perform the SRR calculation
    #from rdtools.soiling import soiling_srr
    cl = 68.2
    sr, sr_ci, soiling_info = soiling_srr(df_BDfilt_dayfilt_daily_mean_series,daily_irr,confidence_level=cl)
    #################################
    # Calculate and view a monthly soiling rate summary
    from rdtools.soiling import monthly_soiling_rates
    monthly_soiling_summary = monthly_soiling_rates(soiling_info['soiling_interval_summary'],
                      confidence_level=cl)
    return [sr, sr_ci, soiling_info, monthly_soiling_summary]

############################
##### plot

def plot_soiling(df_BDfilt_dayfilt_daily_mean_series, soiling_info):
    #####
    fig = rdtools.plotting.soiling_interval_plot(soiling_info, df_BDfilt_dayfilt_daily_mean_series);

    # Plot Monte Carlo realizations of soiling profiles
    fig = rdtools.plotting.soiling_monte_carlo_plot(soiling_info, df_BDfilt_dayfilt_daily_mean_series, profiles=200);

    point_color=None
    profile_color='r'
    point_alpha=0.5
    profile_alpha=0.5
    ymin=0.8
    ymax=1.05
    ####
    sratio = soiling_info['soiling_ratio_perfect_clean']*soiling_info['renormalizing_factor']

    fig, ax = plt.subplots(figsize=(8,6))
    renormalized = df_BDfilt_dayfilt_daily_mean_series / soiling_info['renormalizing_factor'] # blue (daily_raw)
    ax.plot(df_BDfilt_dayfilt_daily_mean_series.index,df_BDfilt_dayfilt_daily_mean_series,'o',alpha=point_alpha,color=point_color)
    ax.plot(sratio.index, sratio, 'o',color=profile_color,alpha=profile_alpha) # red
    ax.set_ylim(ymin, ymax)
    ax.set_yticks(np.arange(ymin,ymax,0.1),minor=False)
    ax.set_ylabel('EPI (output/calculated)',fontsize=14);
    fig.autofmt_xdate()

    ##############################
    # View a histogram of the valid soiling rates found for the data set
    fig = rdtools.plotting.soiling_rate_histogram(soiling_info, bins=50)

##############################
####### Save files ########
def save_data(soiling_info, monthly_soiling_summary, working_dir):
    working_dir += "soiling/"
    pathlib.Path(working_dir).mkdir(parents=True, exist_ok=True)
    sratio = soiling_info['soiling_ratio_perfect_clean']
    sratio.to_csv(working_dir + "EPI_soiling_norm_park1.csv")

    soiling_summary = soiling_info['soiling_interval_summary']
    soiling_summary.to_csv(working_dir + "soiling_summary_park1.csv")

    monthly_soiling_summary.to_csv(working_dir + "monthly_soiling_summary_park1.csv")

########################

def run_soiling_estimation(df, df_env, data_prep = False, working_dir = None):
    if data_prep is True:
        df, df_env = prep_data(df, df_env)

    sr, sr_ci, soiling_info, monthly_soiling_summary = estimate_soiling(df, df_env)
    plot_soiling(df, soiling_info)

    if working_dir is not None:
        save_data(soiling_info, monthly_soiling_summary, working_dir)
