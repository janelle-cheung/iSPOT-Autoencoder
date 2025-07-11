import json
import torch
from datetime import datetime
from src.data import train_val_split, make_eeg_dataloader_from_dict
from src.hyperparam_search.unsupervised_ae_search import unsupervised_ae_search
from src.hyperparam_search.semisupervised_ae_search import semisupervised_ae_search
from src.hyperparam_search.semisupervised_rvae_search import semisupervised_rvae_search
from src.hyperparam_search.hyperparam_configs import *
from src.data import load_train_test_data
from src.configs import  MODELS_DIR, HYPERPARAM_RESULTS_DIR
from src.utils import relative_path_str, setup

"""
Run hyperparameter search for different models:
1. Unsupervised Autoencoder
2. Semi-supervised Autoencoder
3. Semi-supervised RVAE
4. Unsupervised RVAE (to be implemented)

Hyperparameter grids are defined in `hyperparam_configs.py`.
Best models/results from each run are saved to 'MODELS_DIR' and 'HYPERPARAM_RESULTS_DIR'
with timestamps.
"""

def run_search(train_loader=None, val_loader=None): 
    # 1) Unsupervised autoencoder
    best_model, best_config, best_score, all_results = unsupervised_ae_search(
        train_loader, val_loader, unsup_ae_search_space
    )
    save_search_results(all_results, "unsupervised_ae")
    save_best_model(best_model, best_config, best_score, "unsupervised_ae")
    
    # 2) Semi-supervised autoencoder
    best_model, best_config, best_score, all_results = semisupervised_ae_search(
        train_loader, val_loader, semi_ae_search_space
    )
    save_search_results(all_results, "semisupervised_ae")
    save_best_model(best_model, best_config, best_score, "semisupervised_ae")

    # 3) Semi-supervised RVAE 
    best_model, best_config, best_score, all_results = semisupervised_rvae_search(
        train_loader, val_loader, semi_rvae_search_space
    )
    save_search_results(all_results, "semisupervised_rvae")
    save_best_model(best_model, best_config, best_score, "semisupervised_rvae")

    # 4) Unsupervised RVAE
    # TO-DO

def save_search_results(results, model_type):
    """Save hyperparameter search results to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{model_type}_hyperparam_search_{timestamp}.json"
    filepath = HYPERPARAM_RESULTS_DIR / filename
    
    # Convert numpy types to native Python types for JSON serialization
    json_results = []
    for result in results:
        json_result = {
            'hyperparams': result['hyperparams'],
            'val_roc_auc': float(result.get('val_roc_auc', 0))
        }
        json_results.append(json_result)
    
    with open(filepath, 'w') as f:
        json.dump({
            'model_type': model_type,
            'search_space': unsup_ae_search_space if 'unsupervised' in model_type else semi_ae_search_space,
            'timestamp': timestamp,
            'results': json_results
        }, f, indent=2)
    
    print(f"Hyper param search results saved to: {relative_path_str(filepath)}")
    return filepath

def save_best_model(model, config, score, model_type):
    """Save the best model and its configuration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save model state dict
    model_filename = f"best_{model_type}_{timestamp}.pth"
    model_path = MODELS_DIR / model_filename
    torch.save(model.state_dict(), model_path)
    
    # Save config and metadata
    config_filename = f"best_{model_type}_{timestamp}_config.json"
    config_path = MODELS_DIR / config_filename
    
    config_data = {
        'model_type': model_type,
        'best_config': config,
        'best_val_score': float(score),
        'timestamp': timestamp,
        'model_file': model_filename,
        'architecture': {
            'input_dim': model.encoder[0].in_features if hasattr(model, 'encoder') else None,
            'latent_dim': config.get('latent_dim'),
            'model_class': model.__class__.__name__
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"Best model saved to: {relative_path_str(model_path)}")
    print(f"Best config saved to: {relative_path_str(config_path)}")
    return model_path, config_path

def get_dataloaders():
    """Get train and validation DataLoaders"""
    all_data = load_train_test_data()
    full_train_dict = all_data['train']
    
    # Further split train data into train and validation sets for hyperparameter search
    train_dict, val_dict = train_val_split(full_train_dict)
    
    # Make DataLoaders
    train_loader = make_eeg_dataloader_from_dict(train_dict)
    val_loader = make_eeg_dataloader_from_dict(val_dict, shuffle=False)
    
    return train_loader, val_loader

if __name__ == "__main__":
    setup()
    train_loader, val_loader = get_dataloaders()
    run_search(train_loader, val_loader)