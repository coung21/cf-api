import torch
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
from torchvision import transforms
import torch.nn.functional as F
import sys
from .unet import UNet


transform_fn = transforms.Compose([
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Model(torch.nn.Module):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.encoder1 = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT).features
        self.encoder2 = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT).features
        self.encoder3 = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT).features
        self.unet = torch.load('model/checkpoints/unet-cf-2.pth', map_location=device, weights_only=False)
        self.fc = torch.nn.Sequential(
            torch.nn.Dropout(p=0.2),
            torch.nn.Linear(3840, 2560),
            torch.nn.ReLU(),
            torch.nn.Linear(2560,1280),
            torch.nn.ReLU(),
            torch.nn.Linear(1280, 5),
        )
        for param in self.encoder1.parameters():
            param.requires_grad = True
        for param in self.encoder2.parameters():
            param.requires_grad = True
        for param in self.encoder3.parameters():
            param.requires_grad = True
        for param in self.unet.parameters():
            param.requires_grad = True


    def forward(self, x): # x: (N, C, H, W)
        symp_mask = self.unet(x / 255.0) #return (N, num_class, h, w)
        symp_mask = symp_mask.argmax(dim=1) # return (N, h, w)
        symp_mask = symp_mask.unsqueeze(1) # return (N, 1, h, w)
        
        symp = torch.where(symp_mask == 2, x, 255).to(torch.uint8) 
        
        color_image = torch.zeros((symp_mask.squeeze(1).size(0), 3, symp_mask.squeeze(1).size(1), symp_mask.squeeze(1).size(2)), dtype=torch.uint8)
        color_image[:, 1, :, :] = (symp_mask.squeeze(1) == 1).byte() * 255  # Set green channel to 255 where class == 1
        color_image[:, 0, :, :] = (symp_mask.squeeze(1) == 2).byte() * 255  # Set red channel to 255 where class == 2
        
        x = x / 255
        symp = symp / 255
        color_image = color_image / 255
        
        x = torch.stack([transform_fn(img) for img in x]).to(self.device)
        symp = torch.stack([transform_fn(img) for img in symp]).to(self.device)
        color_image = torch.stack([transform_fn(img) for img in color_image]).to(self.device)
        
        
        x1 = self.encoder1(x) # return (N, 1280, 7,7)
        x2 = self.encoder2(symp) # return (N, 1280, 7,7)
        x3 = self.encoder3(color_image) # (N, 1280, 7,7)

        x = torch.cat([x1, x2, x3], dim=1) # return (N, 3840, 7,7)

        x = torch.nn.AdaptiveAvgPool2d(1)(x) # return (N, 3840, 1,1)
        x = torch.flatten(x, start_dim=1) # return (N, 3840)
        x = self.fc(x) # return (N, 5)

        return x
    
    

sys.modules['__main__'].Model = Model
sys.modules['__main__'].UNet = UNet
model = torch.load("model/checkpoints/cf_model.pt", map_location=device, weights_only=False)


def _resize_batch(batch):
    img_size = (224, 224)
    batch = batch.permute(0,3,1,2)
    batch = F.interpolate(batch, size=img_size, mode='bilinear', align_corners=False)
    batch = batch.clone().detach().to(torch.uint8)
    return batch # (N, C, H, W)

async def predict(image):
    input = _resize_batch(image)
    input = input.to(device)
    model.eval()
    with torch.no_grad():
        output = model(input)
        prd = output.argmax(dim=1)
         
    return prd

