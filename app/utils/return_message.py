from fastapi import HTTPException

def Success(message, data):
    success = True
    return {"success": success, "message": message, "data": data}

def Failed(status_code: int, detail: str):
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": detail,
        }
    )
    
    