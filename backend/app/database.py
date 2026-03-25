from supabase import create_client
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# SCANS
# =========================

# def create_scan(user_id, device_id):
#     try:
#        response = supabase.table("scans").insert({...}).execute()
#        print("Supabase response:", response)
#     except Exception as e:
#        print("SUPABASE ERROR:", e)
#        raise e
#     scan_id = str(uuid.uuid4())

#     supabase.table("scans").insert({
#         "scan_id": scan_id,
#         "user_id": user_id,
#         "device_id": device_id,
#         "started_at": datetime.utcnow().isoformat(),
#         "completed_at": None,
#         "status": "running"
#     }).execute()

#     return scan_id

def create_scan(user_id, device_id,layer):
    scan_id = str(uuid.uuid4())

    try:
        response = supabase.table("scans").insert({
            "scan_id": scan_id,
            "user_id": user_id,
            "device_id": device_id,
            "layer": layer,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "running"
        }).execute()

        print("Supabase response:", response)

    except Exception as e:
        print("SUPABASE ERROR:", e)
        raise e

    return scan_id


def complete_scan(scan_id):
    supabase.table("scans").update({
        "status": "completed",
        "completed_at": datetime.utcnow().isoformat()
    }).eq("scan_id", scan_id).execute()


# =========================
# FILES
# =========================

def save_file(scan_id, file_path, is_malicious, layer):
    file_id = str(uuid.uuid4())

    supabase.table("files").insert({
        "file_id": file_id,
        "scan_id": scan_id,
        "file_path": file_path,
        "is_malicious": is_malicious,
        "action": None,
        "layer": layer
    }).execute()

    return file_id


def update_file_action(file_id, action):
    supabase.table("files").update({
        "action": action
    }).eq("file_id", file_id).execute()


# =========================
# HELPERS
# =========================

# 

def get_user_by_device(device_id):
    result = supabase.table("devices") \
        .select("user_id") \
        .eq("device_id", device_id) \
        .single() \
        .execute()

    return result.data["user_id"]

def get_layer2_suspicious_files(device_id):
    return supabase.table("files") \
        .select("*, scans!inner(device_id)") \
        .eq("scans.device_id", device_id) \
        .eq("layer", "layer2") \
        .eq("is_malicious", True) \
        .execute().data


def get_layer1_scans(device_id):
    return supabase.table("scans") \
        .select("*") \
        .eq("device_id", device_id) \
        .eq("layer", "layer1") \
        .execute().data