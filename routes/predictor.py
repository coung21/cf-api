from sanic import Blueprint
from sanic.response import json
from utils.image_utils import read_file_as_image
import numpy as np
import torch
from model.sam import sam_preprocess
from model.model import predict

predictor_routes = Blueprint("predictor", url_prefix="/predictor")

@predictor_routes.route("/predict", methods=["POST"])
async def predict_route(request):
    file = request.files.get("file")

    if file is None:
        return json({"error": "No file is attached"}, status=400)

    # Chuyển đổi file body thành Tensor (nếu cần) và xử lý
    image = read_file_as_image(file.body)

    # Kiểm tra nếu `read_file_as_image` trả về một ảnh có định dạng `Tensor`
    if not isinstance(image, torch.Tensor):
        return json({"error": "Failed to process image to Tensor"}, status=500)

    # Thêm batch dimension
    image = image.unsqueeze(0)

    # Xử lý ảnh với hàm `sam_preprocess` nếu cần thiết
    image = sam_preprocess(image.cpu().numpy())
    
    # Model prediction
    result = await predict(image)
    print(result)
    
    return json({"message": "Predictor is working!", "result": result.tolist()})
