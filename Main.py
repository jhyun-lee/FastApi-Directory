from fastapi import FastAPI
from typing import Union




from routers import Share_Dir

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":    
	import uvicorn
	uvicorn.run("Main:app", host="0.0.0.0", port=9080, reload=True) 