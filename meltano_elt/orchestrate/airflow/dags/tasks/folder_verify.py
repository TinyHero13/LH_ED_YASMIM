import os
from datetime import datetime

def folder_verify(path_type):
    today = datetime.today().strftime("%Y-%m-%d")
    path = os.path.join("..", "data", path_type, today)
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    return path