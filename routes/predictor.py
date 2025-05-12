from sanic import Blueprint
from sanic.response import json
from utils.image_utils import read_file_as_image
import torch
from io import BytesIO
from model.sam import sam_preprocess
from model.model import predict
from cloudinary import uploader
from model.validator import validator
import json as jsn
from utils.image_utils import draw_mask
from sanic_ext import openapi

predictor_routes = Blueprint("predictor", url_prefix="/predictor")


@predictor_routes.route("/predict", methods=["POST"])
@openapi.summary("Predict the disease of a leaf")
@openapi.tag("Predictor")
@openapi.body(
    {"multipart/form-data": {"file": "file", "user_id": str, "croods": str}},
    description="Predict the disease of a leaf with an image file and user_id",
)
@openapi.response(
    200,
    {
        "application/json": {
            "result": {"idx": int, "disease": str, "cause": str, "solution": str},
            "confidence": float,
            "image_url": str,
        }
    },
)
async def predict_route(request):
    file = request.files.get("file")
    user_id = request.form.get("user_id")
    croods = request.form.get("croods")
    if file is None:
        return json({"error": "No file is attached"}, status=400)

    val_img = validator.read_file(file.body)
    if val_img is None:
        return json({"error": "Failed to process image"}, status=500)
    val_result = validator.predict(val_img)
    print(val_result)
    if val_result == 0:
        return json({"error": "Invalid image"}, status=400)

    if croods is None:
        return json({"error": "No croods is attached"}, status=400)

    # split lat,long
    croods = croods.split(",")
    lat = float(croods[0])
    long = float(croods[1])

    image = read_file_as_image(file.body)

    if not isinstance(image, torch.Tensor):
        return json({"error": "Failed to process image to Tensor"}, status=500)

    img = image.unsqueeze(0)

    image, mask = sam_preprocess(img.cpu().numpy())

    seg_img = draw_mask(mask, img)

    if seg_img is None:
        return json({"error": "Failed to draw mask"}, status=500)

    buffr = BytesIO()
    seg_img.save(buffr, format="JPEG")
    buffr.seek(0)

    cloudinary_response = uploader.upload(buffr, resource_type="image")

    buffr.close()

    result, confidence = await predict(image)
    print(f"type: {result}")
    print(f"confidence: {confidence}")
    print(f'{cloudinary_response.get("url")}')
    # Trả về kết quả dự đoán
    return json(
        {
            "result": result,
            "confidence": confidence,
            "image_url": cloudinary_response.get("url"),
        }
    )
