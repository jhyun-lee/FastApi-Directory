import subprocess




from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse


import os
import zipfile

PROCESS_SUSPEND_RESUME = 0x0800

from fastapi import UploadFile
from pathlib import Path
import shutil

import datetime

router = APIRouter()
app = FastAPI()



templates = Jinja2Templates(directory="templates")


dirList=[]
fileList=[]


@router.get("/Share", response_class=HTMLResponse)
async def docker(request: Request):
    return templates.TemplateResponse("Share_Dir.html", context={"request": request})
    


@router.post("/dir/Check")
async def CheckDir():

    global dirList
    global fileList

    dirList.clear()
    fileList.clear()

    path='./static/ShareFolder'       
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            user_part = os.path.join(root, dir).split('static')[1]
            dirList.append(user_part)
            

        for file in files:
            user_part = os.path.join(root, file).split('static')[1]
            fileList.append(user_part)

    
    dirList = sorted(dirList)
    fileList = sorted(fileList)


    return dirList,fileList



@router.post("/dir/Count")
async def count_jpg_files(directory : str): ## 이미지 count
    directory="./static"+directory

    all_files = os.listdir(directory)

    jpg_count = 0
    directory_count = 0

    for root, dirs, files in os.walk(directory):
        jpg_count += len([file for file in files if file.lower().endswith(".jpg")])
        directory_count += len(dirs)


    return JSONResponse(content={"jpg_count": jpg_count})
    


@router.post("/dir/mkdir")# 디렉토리 생성
async def mkdir(directory_path : str):

    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
        print(f"디렉토리 '{directory_path}' 생성됨")
    else:
        print(f"디렉토리 '{directory_path}' 이미 존재함")


# 압축
@router.post("/dir/zip")
async def zip(directory_path : str, sort: str):

    if sort=='0': # 파일
        file_name = os.path.basename(directory_path)
        zip_file_path = os.path.join(os.path.dirname(directory_path), f"{os.path.splitext(file_name)[0]}.zip")

        # 압축 실행
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            arcname = os.path.basename(directory_path)
            zipf.write(directory_path, arcname)

    else: # 폴더 압축
        dir_name = os.path.basename(directory_path)
        parent_dir = os.path.dirname(directory_path)

        # 압축 파일 경로
        zip_file_path = os.path.join(parent_dir, dir_name + ".zip")

        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(directory_path, '..')))



@router.post("/dir/Unzip")# 압축해제
async def Unzip(file_path : str):

    extract_to_directory = os.path.dirname(file_path)
    
    with zipfile.ZipFile(file_path, 'r') as zip_ref:

        for file_info in zip_ref.infolist():



            ## 윈도우 환경에서 압축한 파일을 푸는데 문제가 있음
            ## 파일 내일을 
            #file_info.filename = file_info.filename.encode('UTF-8').decode('UTF-8', 'ignore') 
            


            #file_info.filename = file_info.filename.encode('UTF-8').decode('UTF-8', 'ignore') 

                

            zip_ref.extract(file_info, extract_to_directory)
            new_file_path = os.path.join(extract_to_directory, os.path.basename(file_path).split('.')[0])




#파일 업로드
@router.post("/upload_file")
async def upload_file(file: UploadFile,savepath : str):
    # 업로드된 파일 정보 출력

    upload_folder = Path(savepath)## ++ /User 1 ~ 5
    upload_folder.mkdir(parents=True, exist_ok=True)  # 업로드 폴더가 없으면 생성
    
    file_path = upload_folder / file.filename
    

    # 업로드된 파일을 서버에 저장
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)



# 파일 다운로드
@router.get("/download_file")
async def download_file(file_path: str):

    file_path_on_server = Path(file_path)
    print(file_path)

    # 파일이 존재하면 해당 파일을 반환
    if file_path_on_server.exists():
        return FileResponse(file_path_on_server)

    return {"error": "File not found"}



@router.post("/dir/Del") # 삭제 버튼 만들것
async def Del_file(file_path: str):

    Del_command = [
        'rm',
        '-r',
        file_path
    ]
    
    subprocess.check_output(Del_command, text=True)




@router.post("/dir/Sample") # 샘플 보내기
async def ffmpeg_sample(request: Request):
    data = await request.json()
    file_path = data.get('file_path')
    saturation = float(data.get('saturation', 1.0))  
    brightness = float(data.get('brightness', 0.0))  
    contrast = float(data.get('contrast', 1.0))
    #checkVideo=int(data.get('check',0))


    savepath = './static' + file_path


    # 삭제
    file_path='./static/sample.jpg'
    
    try:
        # 파일이 존재하는지 확인
        if os.path.exists(file_path):
            # 파일 삭제
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")
        else:
            print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {str(e)}")

    

    # if checkVideo==1:
        
    # else:
    #     ffmpeg_command = [
    #         'ffmpeg',
    #         '-i', savepath,
    #         '-vf', f'eq=saturation={saturation}:brightness={brightness}:contrast={contrast}',
    #         './static/sample.jpg'
    #     ]


    ffmpeg_command = [  # 비디오에서 1프레임 샘플 전송
        'ffmpeg',
        '-i', savepath,
        '-vf', f'eq=saturation={1+saturation/100}:brightness={brightness/100}:contrast={1+contrast/100}',
        '-frames:v', '1',
        './static/sample.jpg'
    ]

    print("savepath : " +  savepath)
    subprocess.check_output(ffmpeg_command, text=True)


    
@router.post("/dir/Conver") # 파일 변환
async def ffmpeg_Conversion(request: Request):
    data = await request.json()

    file_path = data.get('file_path') #변형할 파일
    saturation = float(data.get('saturation', 1.0))  
    brightness = float(data.get('brightness', 0.0))  
    contrast = float(data.get('contrast', 1.0))
    size = data.get('size','3840x2160')
    bitlayer = data.get('bitlayer',8000)
    codec = data.get('codec','libx264')
    formatstr=data.get('formatstr','MP4')


    print("--------------------------------------------------------")
    print(formatstr)


    savepath = './static' + file_path

    directory = os.path.dirname(savepath)
    last_directory = os.path.basename(savepath)
    
    last_directory=str(last_directory).split('.')[0]
    print("last_directory : ---------------------" + last_directory)

    # 날짜와 시간을 형식에 맞게 포맷팅
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d-%H-%M-%S-%f')


    ffmpeg_command = [
        'ffmpeg',
        '-i', savepath, ## 파일 위치
        '-vf', f'eq=saturation={1+saturation/100}:brightness={brightness/100}:contrast={1+contrast/100}',
        '-s', size,
        '-c:v', codec,
        '-preset', 'medium',
        '-b:v', bitlayer,
        directory+'/'+last_directory+"_"+formatted_datetime+"."+formatstr
    ]

    subprocess.check_output(ffmpeg_command, text=True)






