from fastapi import APIRouter
# from app.database import get_files_by_device, get_scans_by_device
from app.database import get_layer2_suspicious_files, get_layer1_scans

router = APIRouter()

@router.get("/files/{device_id}")
async def fetch_files(device_id: str):
    return get_layer2_suspicious_files(device_id)

@router.get("/scans/{device_id}")
async def fetch_scans(device_id: str):
    return get_layer1_scans(device_id)  