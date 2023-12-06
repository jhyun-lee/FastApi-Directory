
import subprocess
import threading



from fastapi import FastAPI, APIRouter, Depends, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse




import os
import json
import cv2
import psutil
import signal
import ctypes
import datetime
import zipfile

PROCESS_SUSPEND_RESUME = 0x0800



from pathlib import Path
import shutil

router = APIRouter()
app = FastAPI()


templates = Jinja2Templates(directory="templates")


dirList=[]
fileList=[]
username=""


@router.get("/dir", response_class=HTMLResponse)
async def security(request: Request):
    global username
    
    username = request.cookies.get("username")

    if username:
        return templates.TemplateResponse("Dir_Man.html", context={"request": request})
    else:
        return RedirectResponse("/login")
    


# 조회 및 

    


@router.post("/dir/SavePoint")# 실행파일 위치 db저장
async def SavePoint(link : str):
    global username
    session = engine.sessionmaker()
    engine.modify(session,username,link)

    





            

       



#파일 업로드

    




    



   


    


    


