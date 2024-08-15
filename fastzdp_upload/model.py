from sqlmodel import SQLModel, Field
from typing import Optional


class FastZdpUploadFileModel(SQLModel, table=True):
    """文件模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    uuid: str
    suffix: str
    md5: str
    save_dir: str
    path: str
    nickname: str
    size: int
    add_time: int
