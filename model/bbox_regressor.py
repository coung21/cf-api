from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_fpn
import torchvision
import torch
import os


model = fasterrcnn_mobilenet_v3_large_fpn(pretrained=False)
# Modify the box predictor to match the number of classes (1 class + background)
num_classes = 2
in_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = torchvision.models.detection.faster_rcnn.FastRCNNPredictor(in_features, num_classes)

model.to("cuda" if torch.cuda.is_available() else "cpu")

checkpoint_path = 'model/checkpoints/bbox_regressor.pt'
if os.path.exists(checkpoint_path):
    print(f"Loading model from {checkpoint_path}")
    
    if torch.cuda.is_available():
        model.load_state_dict(torch.load(checkpoint_path))
    else:
        model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
else:
    print(f"Checkpoint not found at {checkpoint_path}. Please check the path.")
    
model.eval()  # Set the model to evaluation model