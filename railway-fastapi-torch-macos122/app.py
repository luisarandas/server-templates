# 01-03-2024 luis arandas
# Small FastAPI server for DL image app

import os
import io
import glob
import shutil
import platform

from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from typing import List # integrate with older Python versions I think
from PIL import Image
from torchvision.models import ViT_L_32_Weights, vit_l_32

import logging
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

image_dir = "images"
upload_dir = "uploads"
media_dir = "media" 

os_details = {
    "System": platform.system(),
    "Node": platform.node(),
    "Release": platform.release(),
    "Version": platform.version(),
    "Machine": platform.machine(),
    "Processor": platform.processor(),
    "Python Version": platform.python_version(),
}

logging.info("Operating System Details:")
for detail, value in os_details.items():
    logging.info(f"{detail}: {value}")



def setup_root_app_directory():
    if os.path.exists(media_dir):
        shutil.rmtree(media_dir)
        print(f"Deleted existing directory: {media_dir}")    
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        print(f"Created directory: {image_dir}")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"Created directory: {upload_dir}")


app = FastAPI(title="fastapi-image-app")
setup_root_app_directory()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")


origins = [
    "http://localhost",
    # also add something like "web-production-0x000.eu.railway.app"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def resize_and_save_image(input_path, output_path):
    """
    Resize an image to 512x512 pixels and save it to the specified output path.
    """
    with Image.open(input_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        resized_img = img.resize((512, 512), Image.Resampling.LANCZOS)
        resized_img.save(output_path)
    os.remove(input_path)  # Remove the temporary file



def download_file_from_link(url, filename=None):
    """
    Downloads a file from a given URL and saves it in the 'models' directory.
    Creates the 'models' directory if it does not exist.
    (e.g: download_file_from_link("http://example.com/path/to/model.ckpt", "model.zip"))
    """
    if not filename:
        filename = url.split('/')[-1]
    
    os.makedirs("models", exist_ok=True)
    save_path = os.path.join("models", filename)
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # Raises an HTTPError for bad responses
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        print(f"File downloaded successfully: {save_path}")
    except requests.exceptions.HTTPError as err:
        print(f"Error downloading the file: {err}")




def print_folder_contents(folder_path):
    """
    To inspect server directory on button click
    """
    if os.path.exists(folder_path):
        print(f"Contents of {folder_path}:")
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            print(f" - {file_path}")
    else:
        print(f"Folder {folder_path} does not exist.")



def clear_uploaded_images():
    """
    Clear on client login for simplicity (danger)
    """
    global file_urls
    file_urls = []
    global upload_data
    upload_data = []
    global image_dir
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            file_path = os.path.join(image_dir, filename)
            print(f"Attempting to delete: {file_path}")  # Add logging
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"Deleted: {file_path}")  # Success logging
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")  # Success logging
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}') # Failed logging



def find_last_uploaded_image(images_dir):
    images_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), images_dir)
    image_files = glob.glob(os.path.join(images_path, '*'))
    if not image_files:
        return None  
    latest_image = max(image_files, key=os.path.getmtime)
    return os.path.relpath(latest_image, images_path)




@app.get("/")
def read_root():
    global image_dir

    clear_uploaded_images()
    print_folder_contents(image_dir)
            
    return FileResponse("static/index.html")


@app.post("/uploads/")
def create_upload_file(file: UploadFile = UploadFile(...)):
    return {"filename": file.filename}



@app.post("/uploadfile/")
def create_upload_file(file: UploadFile = UploadFile(...)):
    return {"filename": file.filename}


@app.post("/uploadimages/")
async def upload_images(files: List[UploadFile] = File(...)):
    global upload_data
    global file_urls
    for file in files:
        if file.content_type not in ["image/jpg", "image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail=f"File type {file.content_type} not allowed")

        file_location = f"{image_dir}/{file.filename}"
        temp_file_path = file_location + ".tmp"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        resize_and_save_image(temp_file_path, file_location)
        file_url = f"/{image_dir}/{file.filename}"
        file_urls.append(file_url)
        await file.close()

    return JSONResponse(content={"upload callback": "Files uploaded successfully", "image_urls": file_urls})




@app.post("/process-last-image")
async def process_last_image(image: UploadFile = File(...)):
    try:
        print("Starting classification: ")
        # Same as official PyTorch example:
        weights = ViT_L_32_Weights.DEFAULT # .IMAGENET1K_V1
        model = vit_l_32(weights=weights)
        preprocess = weights.transforms() # Step 2: Initialize the inference transforms
        print("Preprocess object: ", preprocess)
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        batch = preprocess(img).unsqueeze(0) # Step 3: Apply inference preprocessing transforms
        prediction = model(batch).squeeze(0).softmax(0) # Step 4: Use the model and print the predicted category
        class_id = prediction.argmax().item()
        score = prediction[class_id].item()
        category_name = weights.meta["categories"][class_id]
        classification_str = str(f"Category: {category_name}, Score: {100 * score:.1f}%")
        print(classification_str)
        return JSONResponse(content={"processing callback": "worked!", "classification": classification_str})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")

