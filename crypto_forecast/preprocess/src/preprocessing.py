import datetime
import pandas as pd

from utils.utils import TIME_UNIT_DICT

def validate_missing_values(data):

    return data.isnull().sum().sum() == 0


def validate_missing_timestamp(data, time_col, unit='minute', time_freq=1):
        
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])
        
    total_gaps = pd.date_range(
        start=data[time_col].min(),
        end=data[time_col].max(),
        freq=f'{time_freq}{TIME_UNIT_DICT[unit]}'
    )
    
    return len(data) == len(total_gaps)


def validate_duplicate_values(data):
    
    return data.duplicated().sum() == 0


def fill_time_gaps(data, time_col, start_time, end_time, unit='minute', time_freq=1):
    
    if isinstance(start_time, str):
        start_time = pd.to_datetime(start_time)
        
    if isinstance(end_time, str):
        end_time = pd.to_datetime(end_time)
        
    
    total_gaps = pd.date_range(
        start=start_time,
        end=end_time,
        freq=f'{time_freq}{TIME_UNIT_DICT[unit]}'
    )
    
    data = data.copy()
    data = data[~data[time_col].duplicated()]
    data = data.set_index(time_col)
    data = data.reindex(total_gaps)
    
    return data.reset_index(names=time_col)


def fill_missing_values(data, columns, how="mean", fill_value=None):

    if not isinstance(columns, list):
        columns = [columns]

    data = data.copy()

    if fill_value is not None:
        for col in columns:
            data[col].fillna(fill_value, inplace=True)

        return data

    if how == "mean":
        for col in columns:
            data[col].fillna(data[col].mean(), inplace=True)
    elif how == "median":
        for col in columns:
            data[col].fillna(data[col].median(), inplace=True)

    elif how == "min":
        for col in columns:
            data[col].fillna(data[col].min(), inplace=True)

    elif how == "max":
        for col in columns:
            data[col].fillna(data[col].max(), inplace=True)

    return data