from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from torch.utils.data import DataLoader

from src.preparation import TimeseriesDataset, ToTensor
from utils.utils import PROGRESS_BAR_FORMAT


def train(dataset, model, batch_size, num_epochs, learning_rate, device):
    
    X, y = dataset
    
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
        shuffle=True,
        num_workers=0
    )
    
    model.to(device)
    model.train()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    print(('%20s'*3)%('Epoch', 'GPU_Mem', 'Loss'))
    for epoch in range(num_epochs):
        with tqdm(dataloader, total=len(dataloader), bar_format=PROGRESS_BAR_FORMAT) as tq:
            for step, mini_batch in enumerate(tq):
                
                optimizer.zero_grad()
                feat = mini_batch['feature'].to(device)
                label = mini_batch['label'].to(device)
                
                pred = model(feat)
                
                loss = criterion(pred, label)
                loss.backward()
                optimizer.step()
                
                mem = f"{torch.cuda.memory_reserved()/1E9 if torch.cuda.is_available() else 0:.3g}G"
                tq.set_description(('%20s'*3)%(f"{epoch+1}/{num_epochs}", mem, f"{loss.item():.4}"))