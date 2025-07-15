import pandas as pd

from utils.utils import TIME_UNIT_DICT


def amount_of_change_price(data, time_col, feature_cols, unit='day', time_freq=1):

    # dtype check
    if not isinstance(feature_cols, list):
        feature_cols = [feature_cols]

    # copy data
    data = data.copy()

    # check & convert time column to datetime
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])

    # sort by timestamp
    data = data.sort_values(by=time_col).reset_index(drop=True)
    
    # previous time data
    prev = data[[time_col]] - pd.to_timedelta(time_freq, unit)
    prev = prev.merge(data, left_on=time_col, right_on=time_col, how='left')
    
    # calculate difference
    for col in feature_cols:    
        data[f'diff_{col}'] = data[col] - prev[col]

    return data


def amount_of_change_rate(data, time_col, feature_cols, unit='day', time_freq=1):

    # dtype check
    if not isinstance(feature_cols, list):
        feature_cols = [feature_cols]

    # copy data
    data = data.copy()

    # check & convert time column to datetime
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])
    
    # sort by timestamp
    data = data.sort_values(by=time_col).reset_index(drop=True)

    # previous time data
    prev = data[[time_col]] - pd.to_timedelta(time_freq, unit)
    prev = prev.merge(data, left_on=time_col, right_on=time_col, how='left')
    
    # calculate difference
    for col in feature_cols:    
        data[f'ratio_{col}'] = data[col] / prev[col]

    return data