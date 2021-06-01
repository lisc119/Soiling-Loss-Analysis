import pandas as pd

from scripts import (
        process_data,
        calculations,
        apply_filters,
        plotting,
        estimate_soiling
        )

def run_processing_pipeline(
        steps = ['preprocess', 'filter', 'estimate_soiling'],
        power_data_filepath = None,
        environment_data_filepath = None,
        capacity_data_filepath = None,
        yearly_degradation_rate = 0,
        keep_env_info = True,
        save_dir = None,
        window_start = 13,
        window_end = 18,
        **kwargs):

    pd.options.mode.chained_assignment = None
    if 'preprocess' in steps:
        df_output, df_EPI = process_data.preprocess_data(
                power_data_filepath,
                environment_data_filepath,
                capacity_data_filepath,
                yearly_degradation_rate,
                keep_env_info,
                save_dir)

    if 'filter' in steps:
        df_filtered_hour, df_filtered_daily = \
                apply_filters.filter_data(
                        df_output,
                        window_start,
                        window_end,
                        save_dir)

    if 'estimate_soiling' in steps:
        print("\n\nEstimating soiling...\n")
        estimate_soiling.run_soiling_estimation(
                df_filtered_daily.drop(columns = ['Temp_A', 'Temp_P', 'Irradiance']).mean(axis=1),
                df_filtered_daily[['Temp_A', 'Temp_P', 'Irradiance']],
                working_dir = save_dir
                )
