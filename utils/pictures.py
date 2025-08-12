import os
from aiogram.types import FSInputFile

def get_picture(picture_name):
    try:
        picture_path = os.path.join('templates', 'pictures', picture_name)
        
        if not os.path.exists(picture_path):
            print(f"[!] picture {picture_name} not found {picture_path}")
            return None
        
        return FSInputFile(picture_path)
        
    except Exception as e:
        print(f"[!] error during loading picture {picture_name}: {e}")
        return None

def picture_exists(picture_name):
    picture_path = os.path.join('templates', 'pictures', picture_name)
    return os.path.exists(picture_path)
