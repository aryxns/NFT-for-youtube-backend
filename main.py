from thirdweb import thirdwebSdk, SdkOptions, MintArg
from fastapi import FastAPI, File, UploadFile, Response
from pydantic import BaseModel
import base64
import math
import uvicorn
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app, storage

# Init firebase with your credentials
cred = credentials.Certificate("creds.json")
initialize_app(cred, {'storageBucket': 'your bucket URL'})

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    name: str
    url: str
    address: str


@app.post("/mint")
def mint(item: Item):
    print(item.name)
    local_name = item.name+item.address
    local_name = local_name.replace(" ", "") + '.png'
    img = Image.open('test.png')

    now = datetime.now()

    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    draw = ImageDraw.Draw(img)
    spacing = 20
    text = """  You have
  successfully completed the video 
  """ + item.name + """ 
  On Youtube"""

    text2 = """ 
  URL - """ + item.url + """ 
  Minter Address - """ + item.address + """ 
  Datestamp - """ + dt_string

    # drawing text size
    draw.text((8, 8), text, fill="white",
              spacing=spacing, align="left")
    draw.text((8, 180), text2, fill="yellow", spacing=spacing, align="left")
    img.save(local_name)
    with open(local_name, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
        my_data = jsonable_encoder({"image": [my_string]})

    # Put your local file path
    fileName = local_name
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
    blob.make_public()
    print("your file url", blob.public_url)

    sdk = thirdwebSdk(SdkOptions(), "https://polygon-rpc.com")

    sdk.set_private_key("your private key")

    nft_module = sdk.get_nft_module("your NFT Collection module address")

    print(nft_module.mint_to(item.address, MintArg(name=item.name, description="The owner of this NFT has watched a youtube video in its entirety",
          image_uri=blob.public_url, properties={"name": item.name, "url": item.url})))
    return JSONResponse(my_data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
