import time
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from benchmark_dataset import get_dataloaders
from models import VanillaRNNModel, BiRNNModel, LSTMModel, GRUModel, count_parameters

def compute_metrics(y_true, y_pred, num_classes=4):
    """
    Compute accuracy, macro F1, and weighted F1 in pure Python/NumPy.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    acc = np.mean(y_true == y_pred)
    
    f1s = []
    support = []
    
    for c in range(num_classes):
        tp = np.sum((y_true == c) & (y_pred == c))
        fp = np.sum((y_true != c) & (y_pred == c))
        fn = np.sum((y_true == c) & (y_pred != c))
        sup = np.sum(y_true == c)
        support.append(sup)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        f1s.append(f1)
        
    macro_f1 = np.mean(f1s)
    total_support = np.sum(support)
    weighted_f1 = np.sum(np.array(f1s) * np.array(support)) / total_support if total_support > 0 else 0.0
    
    return acc, macro_f1, weighted_f1

def train_and_evaluate_all():
    # Setup configuration
    seq_len = 100
    input_dim = 10
    num_classes = 4
    hidden_dim = 64
    epochs = 25
    lr = 0.003
    batch_size = 64
    num_samples = 2400

    print("--- Starting Sequence Architecture Benchmark ---")
    print(f"Sequence Length: {seq_len} | Hidden Dim: {hidden_dim} | Batch Size: {batch_size}")

    train_loader, val_loader = get_dataloaders(
        num_samples=num_samples, seq_len=seq_len, batch_size=batch_size, num_classes=num_classes, input_dim=input_dim
    )

    models = [
        ("Vanilla RNN", VanillaRNNModel(input_dim, hidden_dim, num_classes)),
        ("Bidirectional RNN", BiRNNModel(input_dim, hidden_dim, num_classes)),
        ("LSTM", LSTMModel(input_dim, hidden_dim, num_classes)),
        ("GRU", GRUModel(input_dim, hidden_dim, num_classes))
    ]

    all_results = {}
    criterion = nn.CrossEntropyLoss()

    for name, model in models:
        print(f"\n================ Training {name} ================")
        optimizer = optim.Adam(model.parameters(), lr=lr)
        param_count = count_parameters(model)
        
        history = {
            "model_name": name,
            "param_count": param_count,
            "train_loss": [],
            "val_loss": [],
            "val_accuracy": [],
            "val_macro_f1": [],
            "val_weighted_f1": [],
            "grad_norms": [],
            "epoch_times": [],
            "inference_time_ms": 0.0
        }

        total_train_start = time.time()

        for epoch in range(epochs):
            model.train()
            epoch_start = time.time()
            running_loss = 0.0
            epoch_grad_norms = []

            for x_batch, y_batch in train_loader:
                optimizer.zero_grad()
                logits = model(x_batch)
                loss = criterion(logits, y_batch)
                loss.backward()

                # Extract gradient norm
                grad_norm = model.get_recurrent_grad_norm()
                epoch_grad_norms.append(grad_norm)

                optimizer.step()
                running_loss += loss.item() * x_batch.size(0)

            epoch_time = time.time() - epoch_start
            train_loss = running_loss / len(train_loader.dataset)
            avg_grad_norm = sum(epoch_grad_norms) / len(epoch_grad_norms)

            # Validation phase
            model.eval()
            val_loss = 0.0
            all_preds = []
            all_targets = []
            infer_start = time.time()

            with torch.no_grad():
                for x_batch, y_batch in val_loader:
                    logits = model(x_batch)
                    loss = criterion(logits, y_batch)
                    val_loss += loss.item() * x_batch.size(0)

                    preds = torch.argmax(logits, dim=1)
                    all_preds.extend(preds.cpu().numpy())
                    all_targets.extend(y_batch.cpu().numpy())

            infer_duration = (time.time() - infer_start) * 1000 / len(val_loader) # avg ms per batch
            val_loss = val_loss / len(val_loader.dataset)
            
            acc, macro_f1, weighted_f1 = compute_metrics(all_targets, all_preds, num_classes=num_classes)

            history["train_loss"].append(round(train_loss, 4))
            history["val_loss"].append(round(val_loss, 4))
            history["val_accuracy"].append(round(acc * 100, 2))
            history["val_macro_f1"].append(round(macro_f1 * 100, 2))
            history["val_weighted_f1"].append(round(weighted_f1 * 100, 2))
            history["grad_norms"].append(round(avg_grad_norm, 6))
            history["epoch_times"].append(round(epoch_time, 3))
            history["inference_time_ms"] = round(infer_duration, 2)

            print(f"Epoch {epoch+1:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
                  f"Val Acc: {acc*100:.2f}% | Macro F1: {macro_f1*100:.2f}% | Grad Norm: {avg_grad_norm:.6f} | Time: {epoch_time:.2f}s")

        history["total_train_time_sec"] = round(time.time() - total_train_start, 2)
        all_results[name] = history

    # Save to json file
    with open("results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print("\nBenchmark complete! Results exported to results.json")
    return all_results

if __name__ == "__main__":
    train_and_evaluate_all()
