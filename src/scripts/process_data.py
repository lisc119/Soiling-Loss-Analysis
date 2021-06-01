import pandas as pd
import numpy as np
import copy
import re

from .calculations import calc_pmax
from .calculations import calc_efficiency
from .utils import save_data, update_progress

from tqdm.auto import tqdm

# e.g.
# power_data_filepath = "/data/raw/Nispera_project/SolarPark1_Jun_2019_Jun2020_string_production.csv"
# env_data_filepath = "/data/raw/SolarPark1_Jun_2019_Jun2020_environmental.csv"

###### Used for progress bar ######
default_steps = [
                'Starting preprocessing',
                'Reading data',
                'Standardizing column names',
                'Merging data',
                'Calculating EPI',
                'Cleaning data',
                'Saving data',
                'Finished'
                ]
###################################

def read_data(power_data_filepath, env_data_filepath, cap_data_filepath):
    df_pow = pd.read_csv(power_data_filepath, delimiter = ';')
    df_env = pd.read_csv(env_data_filepath, delimiter = ',')
    df_cap = pd.read_csv(cap_data_filepath)
    return [df_pow, df_env, df_cap]


def fix_datetime(datetime_col):
    return datetime_col.apply(lambda x: pd.to_datetime(x,format='%Y-%m-%d %H:%M:%S'))


def rename_cols(df):
    #If doing a loop, will need to use inplace=True?
    df.rename(columns={'Temp_Amb_celsius':'Temp_A',
                        'Temp_Panel_celsius': 'Temp_P',
                          'Irradiance_kWm2':'Irradiance',
                          'Irradiance_Wm2':'Irradiance',
                          'number_panels':'Panel_number'
                         }, inplace=True 
                 )
    df.rename(columns = lambda x: re.sub('Inversor', "Inverter", x), inplace=True)
    df.rename(columns = lambda x: re.sub('Inversor', "Inverter", x), inplace=True)
    return df


def merge_dfs(df_env, df_pow):
    index_col = [i for i in set(
        df_env.columns.to_list() + df_pow.columns.to_list()) if "date" in i or "time" in i][0]
    df_env[index_col] = fix_datetime(df_env[index_col])
    df_pow[index_col] = fix_datetime(df_pow[index_col])
    return pd.merge(df_pow, df_env, on=[index_col], how='inner')


def match_df_index(df, df_ref):
    if 'displayname' in df.columns:
        return df.set_index(
                'displayname',
                drop = False
                ).loc[[col for col in df['displayname'] if col+"_(kW)" in df_ref.columns]]
    else:
        return df.loc[df_ref.index][[col for col in df_ref.columns if col in df.columns]]


def clean_df(df_merged, keep_env_info):
    collist = df_merged.columns

    RCBs = collist[collist.str.contains('RCB')]
    Inverters = collist[collist.str.contains('Inverter')]
    strings = collist[collist.str.contains('ST')]
    CBs=collist[collist.str.contains('CB')]
    date_col = list(set(collist[collist.str.contains('date')].to_list() + \
            collist[collist.str.contains('time')].to_list()))[0]
    
    df_merged = df_merged.dropna(subset=['Irradiance'])
    cols_to_drop = Inverters.to_list() + ['irr_T_adj']
    if keep_env_info is False:
        cols_to_drop += ['Temp_A', 'Temp_P', 'Irradiance']
    if len(RCBs) > 0:
        cols_to_drop += RCBs.to_list()

    return df_merged.drop(columns=cols_to_drop).set_index(date_col)


def preprocess_data(
        power_data_filepath = None,
        env_data_filepath = None,
        cap_data_filepath = None,
        keep_env_info = False,
        yearly_degradation_rate = 0,
        save_dir = None):

    pbar = tqdm(
            range(len(default_steps)-1),
            desc = "Initializing",
            bar_format = "{desc}: {percentage:.1f}%|{bar}| {n_fmt}/{total_fmt} [Time elapsed: {elapsed} | Time remaining: {remaining}]"
            )

    update_progress(pbar, default_steps)
    df_pow, df_env, df_cap = read_data(power_data_filepath, env_data_filepath, cap_data_filepath)
    update_progress(pbar, default_steps, message = "Data read successfully.")
    
    for df in [df_pow, df_env, df_cap]:
        rename_cols(df)
    update_progress(pbar, default_steps, message = "Columns renamed.")

    df_cap = match_df_index(df_cap, df_pow)
    df_full = merge_dfs(df_env, df_pow)
    update_progress(pbar, default_steps, "Merged DFs.")

    df_PR = calc_efficiency(df_full, df_cap, yearly_degradation_rate)
    update_progress(pbar, default_steps, "Calculated EPIs.")
    df_full = clean_df(df_full, keep_env_info)
    df_PR = match_df_index(df_PR, df_full)
    update_progress(pbar, default_steps, "Cleaned dataframes.\n")

    if save_dir is not None:
        update_progress(pbar, default_steps, "Saving dataframes...")
        save_data([df_full, df_PR], ["df_output", "df_PR"], save_dir, "preprocessing")

    update_progress(pbar, default_steps, "DONE.")
    return [df_full, df_PR]
