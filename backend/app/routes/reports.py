from fastapi import APIRouter
# from app.database import get_files_by_device, get_scans_by_device

router = APIRouter()

@router.get("/files/{device_id}")
async def fetch_files(device_id: str):
    return get_files_by_device(device_id)

@router.get("/scans/{device_id}")
async def fetch_scans(device_id: str):
    return get_scans_by_device(device_id)