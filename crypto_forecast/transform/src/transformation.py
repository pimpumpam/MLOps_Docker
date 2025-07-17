import os
import pickle
import collections
import pandas as pd

import sklearn
import sklearn.preprocessing


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
        assert 'time_col' in kwargs, f"To split the data based on time, you must assign the name of the time-related column to the \'time_col\' argument."

        if isinstance(kwargs['split_point'], str):
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



class MultiColumnScaler:
    def __init__(self, scaler_name):
        self.scaler_name = scaler_name
        self.scaler_dict = collections.defaultdict(eval(f"sklearn.preprocessing.{scaler_name}"))
        
    def transform(self, data, columns, inplace=False):
        
        if not isinstance(columns, list):
            columns = [columns]
            
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].transform(x.values.reshape(-1, 1)).flatten()
                )
        
        else:
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].transform(x.values.reshape(-1, 1)).flatten()
            )
            
    
    def fit_transform(self, data, columns, inplace=False, save_pkl=False, **kwargs):
        if not isinstance(columns, list):
            columns = [columns]
            
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].fit_transform(x.values.reshape(-1, 1)).flatten()
            )
            
            return data
    
        else:
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].fit_transform(x.values.reshape(-1, 1)).flatten()
            )
            
        if save_pkl:
            with open(os.path.join(kwargs['save_path'], f"{self.scaler_name}_{kwargs['save_name']}.pkl"), 'wb') as f:
                pickle.dump(self.scaler_dict, f)

            
    def inverse_transform(self, data, columns, inplace=False):
        if not isinstance(columns, list):
            columns = [columns]
            
        if not all(key in self.scaler_dict for key in columns):
            raise KeyError(f"One of column in {columns} is not scaled")
        
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].inverse_transform(x.values.reshape(-1, 1)).flatten()
            )
            
            return data

        else:
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].inverse_transform(x.values.reshape(-1, 1)).flatten()
            )