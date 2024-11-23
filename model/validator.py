from torchvision import transforms, models
from torch import nn
import torch
from io import BytesIO
from PIL import Image

device = 'cuda' if torch.cuda.is_available() else 'cpu'

class Validator:
    def __init__(self, device):
        self.model = models.mobilenet_v2(pretrained=True)
        self.model.classifier[1] = nn.Sequential(
            nn.Linear(self.model.last_channel, 1),
            nn.Sigmoid()
        )
        self.model.load_state_dict(torch.load('model/checkpoints/mobilenetv2_leaf_classifier.pth', map_location=device))
        self.model = self.model.to(device)
        
        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
    def predict(self, image):
            image = self.transform(image).to(device)
            image = image.unsqueeze(0)
            
            with torch.no_grad():
                self.model.eval()
                output = self.model(image)
                prob = output.argmax(dim=1)
                prob = prob.item()
                return prob
    
    def read_file(self, data):
        image = Image.open(BytesIO(data)).convert("RGB")
        return image
    

validator = Validator(device)