from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import tempfile

from language_translator import handle_and_process_file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dev.swayhire.com", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload")
async def convert_properties(
    file: UploadFile = File(...),
    code: str = Form(...),
    password: str = Form(...),
    fastmode: str = Form(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploded")
    if password != "whatfix123":
        raise HTTPException(status_code=401, detail="Wrong password, please try again")
    if fastmode == 'false':
        bool_v = False
    else:
        bool_v = True
    temp_dir = tempfile.gettempdir()
    temp_zip_path = os.path.join(temp_dir, file.filename)
    with open(temp_zip_path, "wb") as buffer:
        buffer.write(await file.read())

    return (handle_and_process_file(temp_zip_path, code, bool_v))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
