from sanic import Blueprint
from sanic.response import json
from utils.image_utils import read_file_as_image
import torch
from io import BytesIO
from model.sam import sam_preprocess
from model.model import predict
from cloudinary import uploader
from services.history_service import add_history
from model.validator import validator
import json as jsn
from utils.image_utils import draw_mask
from sanic_ext import openapi
predictor_routes = Blueprint("predictor", url_prefix="/predictor")


@predictor_routes.route("/predict", methods=["POST"])
@openapi.summary("Predict the disease of a leaf")
@openapi.tag("Predictor")
@openapi.body(
    {
        "multipart/form-data": {
            "file": "file",
            "user_id": str,
        }
    },
    description="Predict the disease of a leaf with an image file and user_id"
)
@openapi.response(
    200,
    {"application/json": {
        "result": {
            "idx": int,
            "disease": str,
            "cause": str,
            "solution": str
        },
        "confidence": float,
        "image_url": str
    }}
)
async def predict_route(request):
    file = request.files.get("file")
    user_id = request.form.get("user_id")

    if file is None:
        return json({"error": "No file is attached"}, status=400)

    # val_img = validator.read_file(file.body)
    # if val_img is None:
    #     return json({"error": "Failed to process image"}, status=500)
    # # val_result = validator.predict(val_img)
    # if val_result == 0:
    #     return json({"error": "Invalid image"}, status=400)
    
    
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


    history_data = {
        "user_id": user_id,
        "image_url": cloudinary_response["secure_url"],
        "result": result,
        "confidence": confidence
    }

    error = await add_history(request.app.ctx.db, history_data)
    if error:
        return json({"error": f"Failed to save history: {error}"}, status=400)
    # Load data from data.json
    with open('data.json', 'r', encoding='utf-8') as file:
        pred = jsn.load(file)  # Changed 'data' to 'pred'

    # Find the object with matching idx
    matching_obj = next(
        (item for item in pred if item['idx'] == result), None)
 
    return json({"result": matching_obj, "confidence": confidence ,"image_url": cloudinary_response["secure_url"]})
