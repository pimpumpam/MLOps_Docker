import os
import pickle
import collections

import sklearn
import sklearn.preprocessing


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