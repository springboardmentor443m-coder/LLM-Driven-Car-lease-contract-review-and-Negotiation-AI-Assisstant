from pydantic import BaseModel, validator
from fastapi import UploadFile

class ExtractRequest(BaseModel):
    file: UploadFile
    
    @validator('file')
    def validate_file(cls, v):
        if v.content_type != 'application/pdf':
            raise ValueError('Only PDF files are allowed')
        return v