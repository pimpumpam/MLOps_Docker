import pandas as pd


def is_missing_values_exists(data):
    """
    결측값 존재 여부 확인.

    Args:
        data (pandas.DataFrame): 결측값 판별 대상이 되는 데이터프레임

    Returns:
        (bool): 컬럼 중 1개라도 결측 값이 있으면 True 반환. 결측값이 전혀 없으면 False 반환.
    """

    return data.isnull().sum().sum() > 0


def is_duplicate_values_exists(data):
    """
    중복 값 존재 여부 확인.

    Args:
        data (pandas.DataFrame): 중복값 판별 대상이 되는 데이터프레임

    Returns:
        (bool): 중복된 값이 1개라도 있으면 True 반환. 중복 값이 전혀 없으면 False 반환.
    """
    
    return data.duplicated().sum() > 0


def is_missing_timestamp_exists(data, time_col, unit='T', time_freq=1):
    """
    누락된 시간 정보 존재 여부 확인

    Args:
        data (pandas,DataFrame): 누락 여부 판별을 위한 대상 데이터프레임
        time_col (str): 누락 여부 판별을 위한 대상 시간 컬럼
        unit (str, optional): 누락 정보 확인을 위한 시간 단위. Defaults는 'T'로 '분'을 의미.
        time_freq (int, optional): 누락 정보 확인을 위한 시간 계수 단위. Defaults는 1.

    Returns:
        (bool): 누락 값이 존재하면 True, 존재하지 않으면 False 반환.
    """
        
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])
        
    total_gaps = pd.date_range(
        start=data[time_col].min(),
        end=data[time_col].max(),
        freq=f'{time_freq}{unit}'
    )
    
    return len(data) != len(total_gaps)


def fill_time_gaps(data, time_col, start_time, end_time, unit='T', time_freq=1):
    
    if isinstance(start_time, str):
        start_time = pd.to_datetime(start_time)
        
    if isinstance(end_time, str):
        end_time = pd.to_datetime(end_time)
        
    
    total_gaps = pd.date_range(
        start=start_time,
        end=end_time,
        freq=f'{time_freq}{unit}'
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