from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from typing import Annotated
from utils.image_utils import read_file_as_image, draw_mask
from model.sam import sam_preprocess
from model.model import model_predict
from cloudinary import uploader
from model.validator import validator
import torch
from io import BytesIO
from PIL import Image
import logging
import json
from services.history_service import add_history
predictor_router = APIRouter()
MAX_FILE_SIZE_MB = 5


@predictor_router.post("/predict")
async def predict_route(
    request: Request,
    file: UploadFile,
    user_id: Annotated[str, Form()],
    croods: Annotated[str, Form()],
):
    try:
        content = await file.read()

        # Check file size
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File size exceeds limit")

        # Validate image
        val_img = await run_in_threadpool(validator.read_file, content)
        if val_img is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        # val_result = await run_in_threadpool(validator.predict, val_img)
        # if val_result == 0:
        #     raise HTTPException(status_code=400, detail="Image is not acceptable")

        # Validate and parse coordinates
        try:
            lat, long = map(float, croods.strip().split(","))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid coordinates format")

        # Convert image to tensor
        image_tensor = await run_in_threadpool(read_file_as_image, content)
        if not isinstance(image_tensor, torch.Tensor):
            raise HTTPException(status_code=500, detail="Image conversion failed")

        img = image_tensor.unsqueeze(0)

        # Preprocess and draw mask (inference)
        with torch.no_grad():
            image_np, mask = sam_preprocess(img.cpu().numpy())
        seg_img = draw_mask(mask, img)

        if seg_img is None:
            raise HTTPException(status_code=500, detail="Failed to draw mask")

        # Upload to cloud
        buffr = BytesIO()
        seg_img.save(buffr, format="JPEG")
        buffr.seek(0)
        cloudinary_response = await run_in_threadpool(
            uploader.upload, buffr, resource_type="image"
        )
        buffr.close()
        
        image = Image.fromarray(image_np[0].astype("uint8")).convert("RGB")
        # image.save("model/test/test.jpg")

        # Model prediction
        result, confidence = await model_predict(image)
        print(f"Result: {result}, Confidence: {confidence}")
        
        
        # Save history
        history_data = {
            "user_id": user_id,
            "image_url": cloudinary_response.get("url"),
            "result": result,
            "confidence": confidence,
            "croods": [lat, long],
        }
        error = await add_history(request.app.db, history_data)
        
        with open("data.json", "r", encoding="utf-8") as f:
            pred = json.load(f)
        matching_obj = next((item for item in pred if item["idx"] == result), None)
        return JSONResponse(
            {
                "result": matching_obj,
                "confidence": confidence,
                "image_url": cloudinary_response.get("url"),
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception("Unexpected server error")
        raise HTTPException(status_code=500, detail="Internal server error")
