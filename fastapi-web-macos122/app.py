# FastAPI Web Server - Clean Template
# Cross-platform server template for file handling and static file serving

import os
import shutil
import platform

from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from typing import List
from PIL import Image

import logging

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

app = FastAPI(title="FastAPI Web Server")
setup_root_app_directory()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://0.0.0.0",
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
    Clear on client login for simplicity
    """
    global file_urls
    file_urls = []
    global upload_data
    upload_data = []
    global image_dir
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            file_path = os.path.join(image_dir, filename)
            print(f"Attempting to delete: {file_path}")
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    print(f"Deleted: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

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

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Server is running"}

@app.get("/info")
def server_info():
    """Server information endpoint"""
    return {
        "title": "FastAPI Web Server",
        "version": "0.1.0",
        "status": "running",
        "os_info": os_details
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

