import torch
import torch.nn as nn


class GRULayer(nn.Module):
    
    def __init__(self, cfg_model):
        super(GRULayer, self).__init__()
        
        self.cfg_model = cfg_model
        self.model = nn.ModuleList()
        
        for idx, (module, args) in enumerate(cfg_model.rnn_layer):
            layer = eval(module)(*args)
            
            self.model.append(layer)
        
    def forward(self, x):
        
        h = torch.zeros(
            self.cfg_model.gru_num_layers,
            x.size(0),
            self.cfg_model.gru_hidden_dims
        )
        
        for layer in self.model:
            x, h = layer(x, h)
            
        return x    