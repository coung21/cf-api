from torchvision import transforms
from torchvision.models import MobileNet_V2_Weights, mobilenet_v2
from torch import nn
import torch
from io import BytesIO
from PIL import Image

device = 'cuda' if torch.cuda.is_available() else 'cpu'

class Validator:
    def __init__(self, device):
        self.model = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
        # self.model = mobilenet_v2(pretrained=True)
        self.model.classifier[1] = nn.Linear(self.model.last_channel, 1)
        self.model.load_state_dict(torch.load('model/checkpoints/leaf_disease_model_mobilenetv2.pth', map_location=device))
        self.model = self.model.to(device)
        
        self.transform = transforms.Compose([
    transforms.RandomResizedCrop((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])
        
    def predict(self, image):
            image = self.transform(image).to(device)
            image = image.unsqueeze(0)
            
            with torch.no_grad():
                output = self.model(image)
                prob = output.item()
                pred = 1 if prob > 0.5 else 0
                print(pred)
                return pred
    
    def read_file(self, data):
        image = Image.open(BytesIO(data)).convert("RGB")
        return image
    

validator = Validator(device)