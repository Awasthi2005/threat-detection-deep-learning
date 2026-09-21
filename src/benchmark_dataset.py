import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

class SequentialPatternDataset(Dataset):
    """
    Synthetic sequence classification dataset designed to benchmark recurrent models
    on long-range sequence dependencies.
    
    Task Description:
    Each sequence consists of T timesteps of d-dimensional vectors.
    Key signal tokens are placed near the beginning (timesteps 0 to k),
    followed by noise timesteps up to sequence length T.
    The target label depends on the relation between early key signals and late trigger signals.
    
    This explicitly forces models to backpropagate gradients over T timesteps,
    causing Vanilla RNN to suffer from vanishing gradients if T is large (e.g., T=100),
    whereas LSTM and GRU maintain gradient flow via gating mechanisms.
    """
    def __init__(self, num_samples=2000, seq_len=100, num_classes=4, input_dim=10, seed=42):
        super().__init__()
        np.random.seed(seed)
        torch.manual_seed(seed)
        
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.num_classes = num_classes
        self.input_dim = input_dim
        
        self.X, self.y = self._generate_data()

    def _generate_data(self):
        X = np.random.randn(self.num_samples, self.seq_len, self.input_dim).astype(np.float32) * 0.1
        y = np.zeros(self.num_samples, dtype=np.int64)
        
        for i in range(self.num_samples):
            # Class signal determined by early pattern in first 5 timesteps
            cls = np.random.randint(0, self.num_classes)
            y[i] = cls
            
            # Key feature pattern in timesteps 0..4
            pattern_val = (cls + 1) * 1.5
            X[i, 0:5, cls % self.input_dim] += pattern_val
            
            # Distractor noise added in middle sequence timesteps
            X[i, 20:80, :] += np.random.randn(60, self.input_dim).astype(np.float32) * 0.2
            
            # Late trigger pattern in last 5 timesteps correlated with early pattern
            X[i, -5:, (cls + 1) % self.input_dim] += pattern_val * 0.8

        return torch.tensor(X), torch.tensor(y)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def get_dataloaders(num_samples=2400, seq_len=100, batch_size=64, num_classes=4, input_dim=10):
    train_size = int(0.75 * num_samples)
    val_size = num_samples - train_size
    
    dataset = SequentialPatternDataset(num_samples=num_samples, seq_len=seq_len, num_classes=num_classes, input_dim=input_dim)
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    return train_loader, val_loader

def calculate_sequence_metrics(seq_len=100, input_dim=10, hidden_dim=64, num_classes=4, decay_rate=0.95):
    """
    Utility function to enter sequence values and calculate parameter counts,
    gradient decay, and memory footprint across all 4 architectures.
    """
    from models import calculate_model_specs
    specs = calculate_model_specs(
        seq_len=seq_len,
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        num_classes=num_classes,
        spectral_radius=decay_rate
    )
    
    print("================ Sequence Architecture Calculator ================")
    print(f"Inputs: Seq Len={seq_len} | Input Dim={input_dim} | Hidden Dim={hidden_dim} | Classes={num_classes} | Decay Rate={decay_rate}")
    print("-" * 75)
    print(f"{'Architecture':<20} | {'Parameters':<12} | {'FLOPs / Item':<15} | {'Memory (KB)':<12} | {'Grad Retention':<15}".lstrip())
    print("-" * 75)
    for model_name in ["Vanilla RNN", "Bidirectional RNN", "LSTM", "GRU"]:
        p = specs["params"][model_name]
        f = specs["flops"][model_name]
        m = specs["memory_kb"][model_name]
        g = specs["gradient_retention"][model_name]
        print(f"{model_name:<20} | {p:<12,d} | {f:<15,d} | {m:<12.2f} | {g:<15}".lstrip())
    print("-" * 75)
    return specs


def calculate_from_image_dims(width, height, channels=3, mode='width-is-t', hidden_dim=128, num_classes=10):
    """
    Computes sequence parameters, FLOPs, and gradient risks from image dimensions.
    Modes:
      - 'width-is-t': Sequence T = Width, Feature Vector d = Height * channels
      - 'height-is-t': Sequence T = Height, Feature Vector d = Width * channels
      - 'patches': Sequence T = (W/16 * H/16), Feature Vector d = 16 * 16 * channels
    """
    if mode == 'width-is-t':
        T = width
        d = height * channels
    elif mode == 'height-is-t':
        T = height
        d = width * channels
    else: # patches 16x16
        T = max(1, width // 16) * max(1, height // 16)
        d = 16 * 16 * channels

    return calculate_sequence_metrics(seq_len=T, input_dim=d, hidden_dim=hidden_dim, num_classes=num_classes)

if __name__ == "__main__":
    calculate_sequence_metrics(seq_len=100, input_dim=10, hidden_dim=64, num_classes=4)


