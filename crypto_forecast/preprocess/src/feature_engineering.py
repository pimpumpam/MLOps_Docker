import pandas as pd

from utils.utils import TIME_UNIT_DICT


def amount_of_change_price(data, time_col, feature_cols, unit='day', time_freq=1):
    """
    이전 시점과의 변화 차이 산출

    Args:
        data (pandas.DataFrame): 변화 차이 산출을 위한 데이터프레임.
        time_col (str): 시점 차이를 계산하기 위한 시간 컬럼.
        feature_cols (str, list): 변화 차이 산출 대상이 되는 컬럼.
        unit (str, optional): 비교 대상이 되는 시점의 시간 단위. 'day'인 경우 하루 전 데이터와 차이 산출. Defaults to 'day'.
        time_freq (int, optional): 비교 대상이 되는 시점의 시간 계수. Defaults to 1.

    Returns:
        data(pandas.DataFrame): 변화 차이가 산출 된 데이터프레임. 기존 feature_cols 할당 된 컬럼 명 앞에 'diff_'가 붙음.
    """

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
    """
    이전 시점과의 변화량 산출

    Args:
        data (pandas.DataFrame): 변화량 산출을 위한 데이터프레임.
        time_col (str): 시점 차이를 계산하기 위한 시간 컬럼 명.
        feature_cols (str, list): 변화량 산출 대상이 되는 컬럼
        unit (str, optional): 비교 대상이 되는 시점의 시간 단위. 'day'인 경우 하루 전 데이터와 차이 산출. Defaults to 'day'.
        time_freq (int, optional): 비교 대상이 되는 시점의 시간 계수. Defaults to 1.

    Returns:
        data(pandas.DataFrame): 변화 차이가 산출 된 데이터프레임. 기존 feature_cols 할당 된 컬럼 명 앞에 'ratio_'가 붙음.
    """

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