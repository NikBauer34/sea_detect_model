from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import json
from model import get_bird
import requests
import cv2
import os
import time
import uvicorn
import tempfile
import shutil
app = FastAPI()
origins = [
    # разрешенные источники
   "https://sea-front.vercel.app",
   "https://sea-bot.onrender.com"
]

app.add_middleware(
    # сначапо все запрещаем    
    CORSMiddleware,
    # потом начинаем разрешать необходимое
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
freeze_list = []
IMAGEDIR = "inputs/"
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )
@app.get('/')
def here():
    return {'hvvh':'bjb'}
@app.get('/clear/')
def clear():
    if not os.path.exists('inputs'):
        os.makedirs('inputs')
    folder = 'inputs'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    return {'data': 'ok'}
@app.post('/remove/')
def remove_from_list(camera_name = Form(...)):
    global freeze_list
    if camera_name in freeze_list:
      freeze_list.remove(camera_name)
      print(f"{camera_name} removed!")
      print(freeze_list)
      return {'data': 'no'}
@app.post('/upload_video/')
async def upload(file: UploadFile = File(...)):
    contents = await file.read()

    with open(f"videos/{file.filename}", "wb") as f:
        f.write(contents)

    # Открываем видео с помощью OpenCV
    cap = cv2.VideoCapture(f"videos/{file.filename}")
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # Если это пятый кадр, отправляем его на указанный URL
        if frame_count % 5 == 0:
            _, img_encoded = cv2.imencode('.jpg', frame)
            values={'camera_name': 'camera1', 'gps': [5, 5]}
            response = await requests.post('https://sea-bot.onrender.com/upload', files={'frame': img_encoded.tobytes()}, data=values)
            print('hvhvvvh')

    cap.release()
    return {"message": "Все кадры отправлены успешно!"}
@app.post('/upload/')
async def upload_video(img: UploadFile = File(...), camera_name = Form(...), gps = Form(...)):
    global freeze_list
    print(freeze_list)
    with open('data.json', 'r') as file:
        data = json.load(file)
    
    # img.filename = f"new.jpg"
    print(data)
    print(img)
    message = 'skipped'
    contents = await img.read()

    with open(f"{IMAGEDIR}{img.filename}", "wb") as f:
        f.write(contents)
    if not camera_name in freeze_list:
        pred = get_bird(f"{IMAGEDIR}{img.filename}")
        message = pred[1]
        if pred[0] == True:
            if camera_name in data:
                freeze_list.append(camera_name)
                files={'files': open(f"{IMAGEDIR}{img.filename}", "rb")}
                values={'camera_name': camera_name, 'gps': gps, 'chat_id': data[camera_name]}
                r = requests.post('https://sea-bot.onrender.com/upload_file', files=files, data=values)
                print(values)
    
    return {'data': message}
#http://127.0.0.1:70/ типа так
if __name__ == "__main__":
    if not os.path.exists('inputs'):
        os.makedirs('inputs')
    folder = 'inputs'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    uvicorn.run('server:app', host="0.0.0.0", port=70)