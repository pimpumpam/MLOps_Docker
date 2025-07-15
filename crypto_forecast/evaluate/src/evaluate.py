import numpy as np
from tqdm import tqdm

import torch
from torchvision import transforms
from torch.utils.data import DataLoader

from src.preparation import TimeseriesDataset, ToTensor
from utils.utils import PROGRESS_BAR_FORMAT


def evaluate(dataset, model, batch_size, device):
    
    pred = []
    truth = []
    X, y = dataset
    model = model.to(device)
    model.eval()
    
    if len(X.shape)==2:
        X = np.expand_dims(X, 0)
    
    if len(y.shape)==2:
        y = np.expand_dims(y, 0)
    
    
    dataset = TimeseriesDataset(
        feat=X,
        label=y,
        transform=transforms.Compose([
            ToTensor()
        ])
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    print(('%20s'*3)%('Iteration', 'GPU_Mem', ''))
    with torch.no_grad():
        with tqdm(dataloader, total=len(dataloader), bar_format=PROGRESS_BAR_FORMAT) as tq:
            for step, mini_batch in enumerate(tq):
                
                feat = mini_batch['feature'].to(device)
                label = mini_batch['label'].to(device)
                pred_ = model(feat)
                
                pred.extend(pred_.detach().cpu().tolist())
                truth.extend(label.detach().cpu().tolist())
                
                mem = f"{torch.cuda.memory_reserved()/1E9 if torch.cuda.is_available() else 0:.3g}G"
                tq.set_description(('%20s'*3)%(f"{step+1}/{len(dataloader)}", mem, f" "))
                
    return pred, truth
                
                
                