from fastapi import FastAPI, File, UploadFile
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from io import BytesIO
from PIL import Image

model = load_model("washroom.h5")

app = FastAPI()


def preprocess_image(img_bytes, img_size=(224, 224)):
    img = Image.open(BytesIO(img_bytes))  
    img = img.resize(img_size)
    img_array = np.array(img) 
    img_array = np.expand_dims(img_array, axis=0)  
    img_array = img_array / 255.0  
    return img_array

def predict_image(img_bytes):
    img_array = preprocess_image(img_bytes)
    prediction = model.predict(img_array)
    if prediction[0][0] > 0.5:
        result = "Unclean"
    else:
        result = "Clean"
    return result

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    img_bytes = await file.read()
    
    result = predict_image(img_bytes)

    return {"prediction": result}


