import torch.nn as nn

from models.rnn import GRULayer
from models.linear import LinearLayer


class Model(nn.Module):
    
    def __init__(self, cfg_model):
        super(Model, self).__init__()
        
        self.cfg_model = cfg_model
        self.rnn_layer = GRULayer(cfg_model)
        self.linear_layer = LinearLayer(cfg_model)
        
    def forward(self, x):
        out = self.rnn_layer(x) # batch x seq x hidden
        out = out.reshape(out.size(0), -1) # batch x (seq * hidden)
        out = self.linear_layer(out) # batch x (pred_seq * out_feat)
        out = out.reshape(out.size(0), -1, self.cfg_model.output_feature_dims)
        
        return out
        