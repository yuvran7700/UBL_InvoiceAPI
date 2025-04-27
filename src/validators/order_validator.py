from fastapi import UploadFile

async def check_if_file_empty(file: UploadFile) -> bool:
    content = await file.read()
    file.file.seek(0) 
    return len(content.strip()) == 0