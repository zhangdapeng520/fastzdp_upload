import hashlib
import os

def get_suffix(file_path):
    """获取文件后缀"""
    _, file_extension = os.path.splitext(file_path)
    return file_extension

def get_md5(data_bytes):
    """获取MD5值"""
    md5_hash = hashlib.md5()
    md5_hash.update(data_bytes)
    return md5_hash.hexdigest()
