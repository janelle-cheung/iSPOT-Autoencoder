import itertools
import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score
from src.models import UnsupervisedAutoencoder
from src.training.unsupervised_ae import train_unsupervised_autoencoder
from src.data.data_utils import extract_latent_features
from src.training.logreg import train_and_evaluate_logreg
from src.configs import N_EPOCHS

def unsupervised_ae_search(train_loader, val_loader, search_space, n_epochs=N_EPOCHS):
    """
    Runs grid search over the search_space and returns best model/config/score.
    
    Hyperparameters:
    - latent_dim: Dimension of the latent space
    - dropout_rate: Dropout rate for the autoencoder
    - lr: Learning rate for training
    """
    n_configs = np.prod([len(v) for v in search_space.values()])
    print("\n" + "=" * 50)
    print("HYPERPARAMETER SEARCH: UNSUPERVISED VANILLA AUTOENCODER WITH L1 REGULARIZATION")
    print(f"Num configurations: {n_configs}")
    print("=" * 50)
    
    best_score = -np.inf
    best_config = None
    best_model = None
    all_results = []

    keys = list(search_space.keys())
    for i, values in enumerate(itertools.product(*[search_space[k] for k in keys])):
        hyperparams = dict(zip(keys, values))

        print(f"\nConfiguration {i+1}/{n_configs}. Hyperparams:")
        for key, value in hyperparams.items():
            print(f"  {key:15s}: {value}")

        model = UnsupervisedAutoencoder(
            latent_dim=hyperparams['latent_dim'],
            dropout_rate=hyperparams['dropout_rate']
        )
        model = train_unsupervised_autoencoder(
            model, train_loader, n_epochs=n_epochs, lr=hyperparams['lr']
        )

        train_X, train_y, patient_ids = extract_latent_features(model, train_loader)
        val_X, val_y, patient_ids = extract_latent_features(model, val_loader)

        _, roc_auc, y_pred = train_and_evaluate_logreg(train_X, val_X, train_y, val_y)

        all_results.append({'hyperparams': hyperparams, 'val_roc_auc': roc_auc})

        if roc_auc > best_score:
            best_score = roc_auc
            best_config = hyperparams
            best_model = model

    print(f"\nBest hyperparameters: {best_config}")
    print(f"Validation ROC-AUC: {best_score:.3f}")
    
    return best_model, best_config, best_score, all_results