class CfgModel:
    name = 'GRU'
    input_feature_dims = 18
    output_feature_dims = 4
    gru_layer = {
        'input_dim':18,
        'hidden_dim': 50,
        'num_layers': 2,
        'bias': True,
        'batch_first': True,
        'architecture': [
            ['nn.GRU', [18, 50, 2, True, True]]
        ]
    }
    linear_layer = {
        'input_dim': 6000, # GRU Hidden x Number of Sequence, hidden
        'output_dim': 240, # hidden, Prediction Sequence x Number of Output Feature
        'architecture': [
            ['nn.Linear', [6000, 1000]],
            ['nn.ReLU', [False]],
            ['nn.Linear', [1000, 240]]
        ]
    }