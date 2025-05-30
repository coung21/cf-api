import numpy as np
from PIL import Image
from io import BytesIO
import torch
from torchvision.utils import draw_segmentation_masks
import matplotlib.pyplot as plt

def read_file_as_image(data) -> np.ndarray:
    image = Image.open(BytesIO(data)).convert("RGB")

    image = image.resize((2048, 1024))

    image = np.array(image)

    image = torch.tensor(image)

    # Thay đổi hình dạng của mảng để phù hợp với đầu vào của mô hình
    # if image.shape[2] == 3:  # Nếu ảnh RGB
    #     image = np.transpose(image, (2, 0, 1))  # Chuyển đổi từ (H, W, C) sang (C, H, W)
    # else:
    #     raise ValueError("Unsupported image format: {}".format(image.shape))

    return image
def resize_batch(batch):
    img_size = (224, 224)
    batch = batch.permute(0,3,1,2)
    batch = torch.nn.functional.interpolate(batch, size=img_size, mode='bilinear', align_corners=False)
    batch = batch.clone().detach().to(torch.uint8)
    return batch # (N, C, H, W)



def draw_mask(mask, img):
    img = img.squeeze(0).permute(2, 0, 1)
    mask = mask.squeeze()
    # print("MASK", mask)
    # print("IMAGE", img.shape)
    
    mask_bool = mask.to(dtype=torch.bool)
    
    segmented_img = draw_segmentation_masks(img, mask_bool, alpha=0.4, colors='red')
    
    segmented_img = segmented_img.permute(1, 2, 0).byte().numpy()
    
    segmented_img = Image.fromarray(segmented_img)
    
    return segmented_img