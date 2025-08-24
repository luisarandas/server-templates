# fastapi-torch-railway
FastAPI deep learning server (deploy on Railway)

1) Deploys a backend with torchvision pre-trained
2) Accepts image input on the front-end
3) Classify and return results (VisionTransformer ViT-L-32)
4) Hosting template image builds 100%, just change ports

```
(Env from requirements.txt:)
$ (win) .\venv\Scripts\activate
$ (ubu) source venv/bin/activate
(Start server local:)
$ uvicorn app:app --host 0.0.0.0 --port 45678
$ http://0.0.0.0:45678/ (or do 127.0.0.1)
(Using railway.json $PORT should be automatic)
```
![example](media/example.png)
