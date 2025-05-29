
import torch
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
import numpy as np
from model.bbox_regressor import model as bbox_regressor
from torchvision.transforms import functional as F
import matplotlib.pyplot as plt
device = "cuda" if torch.cuda.is_available() else "cpu"

sam2_checkpoint = "model/checkpoints/sam2.1_hiera_small.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_s.yaml"

sam2_model = build_sam2(model_cfg, sam2_checkpoint, device=device)

predictor = SAM2ImagePredictor(sam2_model)


def replace_background(img_batch, masks_batch):
    """Replaces the background of an image batch with white using provided masks.

    Args:
        img_batch: A batch of images with shape (N, H, W, 3).
        masks_batch: A batch of masks with shape (N, 1, H, W).

    Returns:
        A batch of images with the background replaced with white.
    """
    # Step 1: Broadcast masks_batch to match the image shape (N, H, W, 3)
    # Reshape masks_batch to (N, H, W) to remove the single channel dimension
    masks_batch_reshaped = masks_batch.squeeze(1)
    # Repeat the mask along the color channel dimension (axis=3) to match the image shape
    masks_batch_broadcasted = np.repeat(masks_batch_reshaped[..., np.newaxis], 3, axis=3)

    # Step 2: Create a white background (255 for each RGB channel)
    white_background = np.ones_like(img_batch) * 255

    # Step 3: Apply the mask to the image batch
    result = np.where(masks_batch_broadcasted, img_batch, white_background)

    return result

def sam_preprocess(images_np):
    
    # print(images_np.shape)
    regressor_input = F.to_tensor(images_np.squeeze(0))
    # regressor_input = images_np.permute(0, 3, 1, 2)  # (N, C, H, W)
    # print(regressor_input.shape)
    regressor_input = regressor_input.to(device)
    
    with torch.no_grad():
        regressor_output = bbox_regressor(regressor_input.unsqueeze(0))  # Add batch dimension
    
    for box in regressor_output[0]['boxes']:
        x_min, y_min, x_max, y_max = box.int().cpu().numpy()
    
    
        
    
    img_batch = [img for img in images_np]

    bbox = np.array([[x_min, y_min, x_max, y_max]])
    bboxs = [bbox] * len(img_batch)
    
    

    
    predictor.set_image_batch(img_batch)

    masks, _, _ = predictor.predict_batch( 
      point_coords_batch=None,
      point_labels_batch=None,
      box_batch=bboxs,
      multimask_output=False,
      )
    masks = np.stack(masks, axis=0) #(N,1,H,W)
    img_batch = np.stack(img_batch, axis=0) #(N,H,W,C)
    images = replace_background(img_batch, masks)
    
  
     # save replaced background image
    # plt.imsave('model/test/test.jpg', images[0].astype(np.uint8))    
    

    return images, torch.tensor(masks, dtype=torch.float32)