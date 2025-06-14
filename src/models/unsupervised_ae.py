import torch
import torch.nn as nn
from pathlib import Path
from src.configs import *

# TO-DO: 

class UnsupervisedAutoencoder(nn.Module):
    def __init__(self, input_dim=AUTOENCODER_INPUT_DIM, latent_dim=LATENT_DIM, 
                 dropout_rate=DROPOUT_RATE):
        super().__init__()
        self.name = 'UnsupervisedAutoencoder'
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, input_dim)
        )
    
    def forward(self, x):
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction, latent