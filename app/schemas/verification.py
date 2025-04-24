from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentInfo(BaseModel):
    file_name: str
    file_type: str
    file_data: str
    uploaded_at: Optional[datetime]

class SpotVerification(BaseModel):
    spot_id: int
    spot_title: str
    spot_description: str
    spot_address: str
    owner_id: str
    identity_proof_document: DocumentInfo
    ownership_proof_document: DocumentInfo
    supporting_document: Optional[DocumentInfo]