import torch
import torch.nn as nn

class VanillaRNNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes, num_layers=1):
        super().__init__()
        self.model_type = 'Vanilla RNN'
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.rnn = nn.RNN(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, nonlinearity='tanh')
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        out, _ = self.rnn(x)  # out: [batch, seq_len, hidden_dim]
        last_out = out[:, -1, :]
        logits = self.fc(last_out)
        return logits

    def get_recurrent_grad_norm(self):
        # Weight recurrent matrices: weight_hh_l0
        grad_norms = []
        for name, param in self.rnn.named_parameters():
            if 'weight_hh' in name and param.grad is not None:
                grad_norms.append(param.grad.norm(2).item())
        return sum(grad_norms) / max(len(grad_norms), 1)


class BiRNNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes, num_layers=1):
        super().__init__()
        self.model_type = 'Bidirectional RNN'
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.rnn = nn.RNN(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, bidirectional=True, nonlinearity='tanh')
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x):
        out, _ = self.rnn(x)  # out: [batch, seq_len, hidden_dim * 2]
        last_out = out[:, -1, :]
        logits = self.fc(last_out)
        return logits

    def get_recurrent_grad_norm(self):
        grad_norms = []
        for name, param in self.rnn.named_parameters():
            if 'weight_hh' in name and param.grad is not None:
                grad_norms.append(param.grad.norm(2).item())
        return sum(grad_norms) / max(len(grad_norms), 1)


class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes, num_layers=1):
        super().__init__()
        self.model_type = 'LSTM'
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        out, (hn, cn) = self.lstm(x)  # out: [batch, seq_len, hidden_dim]
        last_out = out[:, -1, :]
        logits = self.fc(last_out)
        return logits

    def get_recurrent_grad_norm(self):
        grad_norms = []
        for name, param in self.lstm.named_parameters():
            if 'weight_hh' in name and param.grad is not None:
                grad_norms.append(param.grad.norm(2).item())
        return sum(grad_norms) / max(len(grad_norms), 1)


class GRUModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes, num_layers=1):
        super().__init__()
        self.model_type = 'GRU'
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        out, hn = self.gru(x)  # out: [batch, seq_len, hidden_dim]
        last_out = out[:, -1, :]
        logits = self.fc(last_out)
        return logits

    def get_recurrent_grad_norm(self):
        grad_norms = []
        for name, param in self.gru.named_parameters():
            if 'weight_hh' in name and param.grad is not None:
                grad_norms.append(param.grad.norm(2).item())
        return sum(grad_norms) / max(len(grad_norms), 1)


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def calculate_model_specs(seq_len=100, input_dim=10, hidden_dim=64, num_classes=4, spectral_radius=0.95):
    """
    Calculates parameter counts, FLOPs per sequence, gradient decay factor,
    and memory footprint for Vanilla RNN, BiRNN, LSTM, and GRU given arbitrary input specifications.
    """
    # Formulas:
    # Vanilla RNN: 1 * (input_dim * hidden_dim + hidden_dim^2 + 2*hidden_dim) + (hidden_dim * num_classes + num_classes)
    # BiRNN: 2 * (input_dim * hidden_dim + hidden_dim^2 + 2*hidden_dim) + (2*hidden_dim * num_classes + num_classes)
    # LSTM: 4 * (input_dim * hidden_dim + hidden_dim^2 + 2*hidden_dim) + (hidden_dim * num_classes + num_classes)
    # GRU: 3 * (input_dim * hidden_dim + hidden_dim^2 + 2*hidden_dim) + (hidden_dim * num_classes + num_classes)
    
    base_rnn_layer = input_dim * hidden_dim + hidden_dim**2 + 2 * hidden_dim
    fc_single = hidden_dim * num_classes + num_classes
    fc_double = (2 * hidden_dim) * num_classes + num_classes
    
    params = {
        "Vanilla RNN": base_rnn_layer + fc_single,
        "Bidirectional RNN": 2 * base_rnn_layer + fc_double,
        "LSTM": 4 * base_rnn_layer + fc_single,
        "GRU": 3 * base_rnn_layer + fc_single
    }
    
    # FLOPs per item = 2 * params * seq_len (approx multiplication and addition)
    flops = {
        name: 2 * count * seq_len for name, count in params.items()
    }
    
    # Vanishing gradient decay over T timesteps: gamma^T
    vanish_decay_rnn = (spectral_radius ** seq_len)
    vanish_decay_gated = 0.999 ** seq_len # Gated highway retains ~1.0
    
    # Memory footprint in KB (float32 = 4 bytes)
    memory_kb = {
        name: (count * 4) / 1024.0 for name, count in params.items()
    }
    
    return {
        "inputs": {
            "seq_len": seq_len,
            "input_dim": input_dim,
            "hidden_dim": hidden_dim,
            "num_classes": num_classes,
            "spectral_radius": spectral_radius
        },
        "params": params,
        "flops": flops,
        "gradient_retention": {
            "Vanilla RNN": f"{vanish_decay_rnn * 100:.4f}%",
            "Bidirectional RNN": f"{vanish_decay_rnn * 100:.4f}%",
            "LSTM": f"{vanish_decay_gated * 100:.2f}% (Gated Highway)",
            "GRU": f"{vanish_decay_gated * 100:.2f}% (Gated Highway)"
        },
        "memory_kb": memory_kb
    }

