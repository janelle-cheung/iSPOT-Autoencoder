import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from src.configs import *
from src.data import *
from src.utils import *
from src.experiments import *
from torch.utils.data import *

def main():
    # Load data
    data = load_train_test_data()
    train_eeg_dataloader, test_eeg_dataloader = create_eeg_dataloaders(data)

    # Run all experiments
    results = run_all_experiments(data, train_eeg_dataloader, test_eeg_dataloader)

    # Analyze results
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    for experiment_name in results.keys():
        print(f"✓ {experiment_name.replace('_', ' ').title()} - Complete")

if __name__ == '__main__':
    setup()
    main()
