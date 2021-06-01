import pandas as pd
import pickle
from pathlib import Path

from tqdm.auto import tqdm
from time import sleep

def save_data(dataframes, names, root_dir, sub_dir):

    if root_dir[-1] != "/":
                root_dir += "/"

    if sub_dir[-1] != "/":
                root_dir += sub_dir + "/"

    for data, name in zip(dataframes, names):
        try:
            filepath_out = root_dir + name + ".csv"
            Path(root_dir).mkdir(parents=True, exist_ok=True)
            print(f"\tSaving {filepath_out}...")
            data.to_csv(filepath_out)
            print("\tDone.")
        except Exception as e:
            print(e)
            pass


def update_progress(progress_bar:tqdm, steps:list, message:str = None):
    progress_bar.set_description(steps[progress_bar.n])
    if message is not None:
        progress_bar.write(message)
    if progress_bar.n < len(steps):
        progress_bar.update()
    sleep(1)
    pass
