import os
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import seaborn as sns
from tqdm import tqdm
from torch.utils.data import random_split

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

model = nn.Sequential(*list(models.resnet50().children())[:-2])

num_classes = 5
model.avgpool = nn.AdaptiveAvgPool2d((1,1))
model.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
)

model = model.to("cuda" if torch.cuda.is_available() else "cpu")
checkpoint_path = "model/checkpoints/cf_classifier.pt"
if os.path.exists(checkpoint_path):
    print(f"Loading model from {checkpoint_path}")
    if torch.cuda.is_available():
        model.load_state_dict(torch.load(checkpoint_path))
    else:
        model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
else:
    print(f"Checkpoint not found at {checkpoint_path}. Please check the path.")
    
    
# def _resize_batch(batch):
#     img_size = (224, 224)
#     batch = batch.permute(0,3,1,2)
#     batch = F.interpolate(batch, size=img_size, mode='bilinear', align_corners=False)
#     batch = batch.clone().detach().to(torch.float32)  # Ensure the tensor is float32
#     return batch # (N, C, H, W)


    
async def model_predict(image):
    """Predict the class of an image
    Args:
        image_tensor (torch.Tensor): Input image tensor of shape (N, H, W, C)
        tuple: Predicted class index and confidence score
    """
    image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
    image_tensor = image_tensor.to("cuda" if torch.cuda.is_available() else "cpu")
    model.to(image_tensor.device)
    with torch.no_grad():
        model.eval()
        output = model(image_tensor)
        predictions = F.softmax(output, dim=1)
        prd, idx = predictions.max(dim=1)
        confidence = float(f"{prd.item():.3f}")
        label = idx.item()
    return label, confidence