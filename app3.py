from fastapi import FastAPI, Form, WebSocket, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader

from starlette import status
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import HTMLResponse, RedirectResponse

from typing import Union
from typing_extensions import Annotated
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

from datetime import datetime, timedelta

from fastapi.templating import Jinja2Templates

from routers import items, users



import cv2
from ultralytics import YOLO
from PIL import Image



templates = Jinja2Templates(directory="templates")

app.include_router(items.router)
app.include_router(users.router)

SECRET_KEY = "2465d0297a4adac1cf10cc2e330193160a29146d92d4db2305b99cd9d0d86d03"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


users_db = {
	"root": {
		"username": "root",
		"hashed_password": "fakehashedsecret",
		"disabled": False,
	},
	"root2": {
		"username": "root2",
		"hashed_password": "fakehashedsecret2",
		"disabled": True,
	},
}

class Token(BaseModel):
	access_token: str
	token_type: str

class TokenData(BaseModel):
	username: Union[str, None] = None

class User(BaseModel):
	username: str
	disabled: Union[bool, None] = None

class UserInDB(User):
	hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
	return pwd_context.hash(password)


def get_user(db, username: str):
	if username in db:
		user_dict = db[username]
		return UserInDB(**user_dict)

def fake_hash_password(password: str):
	return "fakehashed" + password



def authenticate_user(fake_db, username: str, password: str):
	user = get_user(fake_db, username)
	if not user:
		return False
	if not verify_password(password, user.hashed_password):
		return False
	return user

def fake_decode_token(token):
	user = get_user(users_db, token)
	return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
	if current_user.disabled:
		raise HTTPException(status_code=400, detail="Inactive user")
	return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/items/")
async def read_own_items(current_user: Annotated[User, Depends(get_current_active_user)]):
	return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
	return current_user


@app.get('/')
def redirect_to_login():
	return RedirectResponse(url="/login")





id_info = None
pw_info = None


@app.get('/login')
def login_page():
	global id_info
	id_info = "required" if id_info == None else id_info
	global pw_info
	pw_info = "required" if pw_info == None else pw_info
	html =  f"""
		<h3>Login</h3>
		<div>
		<p>ID:{id_info}</p>
		<p>PW:{pw_info}</p>
		</div>
		<form method="post">
		<input name="username" type="text" placeholder="ID">
		<input name="password" type="text" placeholder="PW">
		<input type="submit" value="login">
		</form>"""
	return HTMLResponse(content=html)






@app.post('/login')
def login(username: str = Form(...), password: str = Form(...)):
	id = "test"
	pw = "test"
	if username == id and password == pw:
		return RedirectResponse(url="/model", status_code=status.HTTP_302_FOUND)
	if username != id:
		global id_info
		id_info = "incorrect"
	if	password != pw:
		global pw_info
		pw_info = "incorrect"
	return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
	




# @app.get('/model', response_class=HTMLResponse)
# def model_page(current_user: Annotated[User, Depends(get_current_active_user)]):
# 	return '''
# 		<h3>Model</h3>
# 		<input type="file" name="model" id="modelFile">
# 		<form method="post">
# 		<input type="submit" value="predict"/>
# 		</form>'''



# @app.post('/model', response_class=HTMLResponse)
# async def model_predict():
# 	model = YOLO("models/yolov8l_230710.pt")
# 	src = 'rtmp://192.168.1.9/play/livetest'
# 	rets = model.predict(src, stream=True)
# 	for ret in rets:
# 		return ret.tojson()








@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	if await websocket.receive_text() == "predict":
		model = YOLO("yolov8s.pt")
		src = 'rtmp://192.168.1.9/play/livetest'
		rets = model.predict(src, stream=True)
		data = None
		try: 
			while True:
				for ret in rets:
					await websocket.send_text(ret.tojson())
		except KeyboardInterrupt:
			pritn("KeyboardInterrupt received. Closing WebSocket.")
		finally:
			await websocket.close()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket</title>
    </head>
    <body>
        <h1>Json</h1>
        <form action="" onsubmit="sendMessage(event)">
            <button>predict</button>
        </form>
		<form action="" onsubmit="sendStop(event)">
			<button>stop</button>
		</form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                ws.send("predict")
                event.preventDefault()
            }
			function sendStop(event) {
				ws.send("stop")
				event.preventDefault()
			}
        </script>
    </body>
</html>
"""


@app.get('/websocket')
async def websocket():
	return HTMLResponse(html)


if __name__ == "__main__":
	import uvicorn
	uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
