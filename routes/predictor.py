from sanic import Blueprint
from sanic.response import json
from utils.image_utils import read_file_as_image
import torch
from model.sam import sam_preprocess
from model.model import predict
from cloudinary import uploader
from services.history_service import add_history

predictor_routes = Blueprint("predictor", url_prefix="/predictor")

@predictor_routes.route("/predict", methods=["POST"])
async def predict_route(request):
    file = request.files.get("file")
    user_id = request.form.get("user_id")

    if file is None:
        return json({"error": "No file is attached"}, status=400)

  
    image = read_file_as_image(file.body)

   
    if not isinstance(image, torch.Tensor):
        return json({"error": "Failed to process image to Tensor"}, status=500)

 
    image = image.unsqueeze(0)


    image = sam_preprocess(image.cpu().numpy())

    result = await predict(image)
    
    cloudinary_response = uploader.upload(file.body)
    
    history_data = {
        "user_id": user_id,
        "image_url": cloudinary_response["secure_url"],
        "result": result.tolist()[0],
    }
    
    error = await add_history(request.app.ctx.db, history_data)
    if error:
        return json({"error": f"Failed to save history: {error}"}, status=400)
    
    return json({"result": result.tolist()[0], "image_url": cloudinary_response["secure_url"]})
