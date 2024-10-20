from sanic import Sanic, response
from sanic_cors import CORS
import numpy as np
import torch
from io import BytesIO
from PIL import Image

app = Sanic(__name__)
CORS(app)

pathURL = "FileModel/model_2_1.pth"

#load model
model = torch.load(pathURL, map_location=torch.device('cpu'), weights_only=False)

model.eval()

#define 5 class in model
CLASS_NAMES = ["healthy", "miner", "rust", "phoma", "cercospora"]


#read file img => convert
def read_file_as_image(data) -> np.ndarray:
    image = Image.open(BytesIO(data))

    image = image.resize((224, 224))

    image = np.array(image) / 255.0  # Chia cho 255 để chuẩn hóa về khoảng [0, 1]

    # Thay đổi hình dạng của mảng để phù hợp với đầu vào của mô hình
    if image.shape[2] == 3:  # Nếu ảnh RGB
        image = np.transpose(image, (2, 0, 1))  # Chuyển đổi từ (H, W, C) sang (C, H, W)
    else:
        raise ValueError("Unsupported image format: {}".format(image.shape))

    return image


#predict img when user upload file img
@app.post("/predict")
async def predict(request):
    file = request.files.get('file')
    if file is None:
        return response.json({"error": "No file provided"}, status=400)

    image = read_file_as_image(file.body)
    img_batch = np.expand_dims(image, axis=0)  # Thêm batch dimension
    img_tensor = torch.tensor(img_batch, dtype=torch.float32)

    with torch.no_grad():
        predictions = model(img_tensor)

    # Kiểm tra kích thước của predictions
    if predictions.dim() == 2 and predictions.size(0) > 0:
        predicted_class_index = torch.argmax(predictions[0]).item()

        print("Predicted Class Index: " + str(predicted_class_index))

        if predicted_class_index < len(CLASS_NAMES):
            predicted_class = CLASS_NAMES[predicted_class_index]
        else:
            predicted_class = "Unknown class"
    else:
        predicted_class = "No predictions made"

    confidence = torch.max(predictions[0]).item() if predictions.dim() == 2 else None

    return response.json({
        'class': predicted_class,
        'confidence': float(confidence) if confidence is not None else None
    })


if __name__ == "__main__":
    app.run(host='localhost', port=8000)
