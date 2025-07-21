import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

import torch
from torch.utils.data import Dataset


def apply_sliding_window(data, time_col, feature_cols, input_seq_len, label_seq_len, **kwargs):

    # dtype check
    if not isinstance(feature_cols, list):
        feature_cols = [feature_cols]
        
    # remove duplicated and NaN row
    data = data.drop_duplicates()
    data = data.dropna()

    # sort by time column
    
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])

        data = data.sort_values(by=time_col).reset_index(drop=True)

    # data sampling
    data_arr = data[feature_cols].values
    
    # set sequence length
    seq_len = input_seq_len + label_seq_len
    
    # apply sliding window
    window_data = sliding_window_view(data_arr, (seq_len,), axis=0).transpose(0, 2, 1)

    # set inputs and labels
    X = window_data[:, :input_seq_len, :].squeeze()
    y = window_data[:, input_seq_len:, :4].squeeze()
    
    return X.copy(), y.copy()


class TimeseriesDataset(Dataset):
    
    def __init__(self, feat, label, transform=None):
        self.feat = feat
        self.label = label
        self.transform = transform
        
    def __len__(self):
        return len(self.feat)
    
    def __getitem__(self, idx):
        
        sample = {
            'feature': self.feat[idx], 
            'label': self.label[idx]
        }
        
        if self.transform:
            sample = self.transform(sample)
            
        return sample
    
    
class ToTensor(object):
    def __call__(self, sample):
        feat, label = sample['feature'], sample['label']

        return {
            'feature': torch.from_numpy(feat).to(torch.float32),
            'label': torch.from_numpy(label).to(torch.float32)
        }