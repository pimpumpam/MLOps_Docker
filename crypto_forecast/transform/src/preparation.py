import pandas as pd

def split_train_test(data, train_ratio, test_ratio=None, **kwargs):
    
    if train_ratio is not None and test_ratio is None:
        train_ratio = train_ratio

    elif train_ratio is None and test_ratio is not None:
        train_ratio = 1-test_ratio

    elif train_ratio is not None and test_ratio is not None:
        if train_ratio+test_ratio != 1:
            print(f"Sum of argument \'train_ratio\' and \'test_ratio\' must be 1")
        elif train_ratio+test_ratio == 1:
            train_ratio = train_ratio
    else:
        if 'split_point' not in kwargs:
            print(f"One of split ratio or split time must be needed")

    # remove duplicated and NaN row
    data = data.drop_duplicates()
    data = data.dropna()
    
    # sort by time column
    if 'time_col' in kwargs:
        if not pd.api.types.is_datetime64_any_dtype(data[kwargs['time_col']]):
            data[kwargs['time_col']] = pd.to_datetime(data[kwargs['time_col']])

        data = data.sort_values(by=kwargs['time_col']).reset_index(drop=True)
    
    # split by time
    if 'split_point' in kwargs:
        if 'time_col' not in kwargs:
            print(f"To split the data based on time, you must assign the name of the time-related column to the \'time_col\' argument.")

        elif isinstance(kwargs['split_point'], str):
            split_point = pd.to_datetime(kwargs['split_point'])

        train_data = data[data[kwargs['time_col']] <= split_point].reset_index(drop=True)
        test_data = data[data[kwargs['time_col']] > split_point].reset_index(drop=True)

        return train_data, test_data
    
    # split by ratio
    else:
        split_point = int(len(data) * train_ratio)

        train_data = data.iloc[:split_point].reset_index(drop=True)
        test_data = data.iloc[split_point:].reset_index(drop=True)

        return train_data, test_data