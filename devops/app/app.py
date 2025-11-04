# Importing Necessary modules
import fastapi
from typing import Annotated, Type
from fastapi import Depends, FastAPI, UploadFile, File,  HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
import uvicorn
from ml.model import model
from PIL import Image
import numpy as np
import io
from io import BytesIO
from pathlib import Path
import yaml
import json
from pydantic import BaseModel, BaseConfig
from fastapi import Response



class SentimentResponse(BaseModel):
    task: str | None = None
    plant: str | None = None
    
# Declaring our FastAPI instance
app = FastAPI()

@app.get('/readme')
def index():
    return {
        "task": "detect or disease",
        "plant": "tomato or cabbage"
    }

app = FastAPI()


users = {
    "admin": {
        "username": "admin",
        "full_name": "admin",
        "email": "admin@example.com",
        "hashed_password": "assert",
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


def get_user(dict_users, username: str):
    if username in dict_users:
        user_dict = dict_users[username]
        return UserInDB(**user_dict)


def decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(users, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    print(token)
    user = decode_token(token)
    print(token, user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = users.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    if not form_data.password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
    
# Defining path operation for root endpoint
@app.get('/')
async def main():
    return {'message': 'Welcome to Agrlink!'}
'''
# Defining path operation for /name endpoint
@app.get("/file/download")
async def download_file():
  return FileResponse(path='/Users/daniilpikurov/Desktop/Agrlink/devops/Evaluation_branch.xlsx', filename='Evaluation_branch.xlsx', media_type='multipart/form-data')
@app.get("/image/download")
async def download_image():
  return FileResponse(path='/Users/daniilpikurov/Desktop/Agrlink/devops/IMG_1066.jpg', filename='image.jpg', media_type='multipart/form-data')
'''

def read_imagefile(data) -> Image.Image:
    image = np.array(Image.open(BytesIO(data)))
    return image
    
@app.post("/file/upload-file")
async def upload_file(current_user: Annotated[User, Depends(get_current_active_user)], file: UploadFile = File(...), task: str | None = None, plant: str | None = None):
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r") as yaml_file:
        config = yaml.load(yaml_file, Loader=yaml.FullLoader)
    yaml_file.close()
    if not task in config["models"]:
        raise HTTPException(status_code=400, detail="Incorrect task")
    if not plant in config["models"][task]:
        raise HTTPException(status_code=400, detail="Incorrect name plant or not found model for {0}".format(plant))
        
    try:
        contents = await file.read()
        image = read_imagefile(contents)
        result = model(image, task, plant)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        await file.close()
    response = {"request": SentimentResponse(
        task=task,
        plant=plant),
        "result": result}
    return response

    
if __name__ == "__main__":
    uvicorn.run(app)

