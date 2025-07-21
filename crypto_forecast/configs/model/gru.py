class CfgModel:

    name = 'GRU'
    output_dims = 4

    gru_input_dims = 18
    gru_hidden_dims = 50
    gru_num_layers = 2
    gru_bias = True
    gru_batch_first = True

    linear_input_dims = 6000
    linear_hidden_dims = 1000
    linear_output_dims = 240

    rnn_layer = [
        ["nn.GRU", [gru_input_dims, gru_hidden_dims, gru_num_layers, gru_bias, gru_batch_first]]
    ]

    linear_layer = [
        ["nn.Linear", [linear_input_dims, linear_hidden_dims]],
        ["nn.ReLU", [False]],
        ["nn.Linear", [linear_hidden_dims, linear_output_dims]]
    ]