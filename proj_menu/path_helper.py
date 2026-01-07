import os
import sys

def get_resource_path(relative_path):
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        
        full_path = os.path.join(base_path, relative_path)
        return full_path
    except Exception as e:
        print(f"ERROR в get_resource_path: {e}")
        return relative_path

def get_writable_path(filename):
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")
        
        full_path = os.path.join(base_path, filename)
        return full_path
    except Exception as e:
        print(f"ERROR в get_writable_path: {e}")
        return filename
