import os
import uuid
import time
import fastzdp_upload
from fastapi import File, UploadFile, Depends, APIRouter, Response, HTTPException, status
from sqlmodel import Session, select, func
from .model import FastZdpUploadFileModel


def get_router(get_db, UPLOAD_FOLDER="data"):
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    router = APIRouter(tags=["fastzdp_upload"])

    @router.post("/fastzdp_upload/upload/", summary="文件上传")
    async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
        # 获取文件名
        filename = file.filename
        uuid_value = str(uuid.uuid4())
        filename = f"{uuid_value}_{filename}"

        # 读取文件内容
        file_content = await file.read()

        # 保存文件到磁盘
        save_file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(save_file_path, 'wb') as f:
            f.write(file_content)

        # 文件信息保存到数据库
        db_file = FastZdpUploadFileModel(
            name=filename,
            uuid=uuid_value,
            suffix=fastzdp_upload.util.get_suffix(filename),
            md5=fastzdp_upload.util.get_md5(file_content),
            save_dir=UPLOAD_FOLDER,
            path=f"{UPLOAD_FOLDER}/{filename}",
            nickname=file.filename,
            size=len(file_content),
            add_time=time.time(),
        )
        db.add(db_file)
        db.commit()

        return {"filename": file.filename}

    @router.get("/fastzdp_upload/download/{uid}/", summary="文件下载")
    def download_file(uid: int, db: Session = Depends(get_db)):
        # 检查文件是否存在
        db_file = db.exec(select(FastZdpUploadFileModel).where(FastZdpUploadFileModel.id == uid)).first()
        if not db_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file is not exist")

        # 获取文件
        file = open(db_file.path, "rb")
        file_content = file.read()
        response = Response(content=file_content, media_type="application/octet-stream")
        filename = f"{db_file.md5}{db_file.suffix}"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        file.close()

        return response

    @router.get("/fastzdp_upload/", summary="文件查询")
    def get_file(
            page: int = 1,
            size: int = 20,
            name: str = "",
            suffix: str = "",
            save_dir: str = "",
            add_time_gte: int = 0,
            add_time_lte: int = 0,
            size_gte: int = 0,
            size_lte: int = 0,
            db: Session = Depends(get_db),
    ):
        """
        分页查询文件
        """

        # 查询
        query = select(FastZdpUploadFileModel)
        # 根据关键字查询
        if name:
            query = query.where(FastZdpUploadFileModel.name.like(name))
        # 根据后缀查询
        if suffix:
            query = query.where(FastZdpUploadFileModel.suffix == suffix)
        # 根据保存目录查询
        if save_dir:
            query = query.where(FastZdpUploadFileModel.save_dir == save_dir)
        # 根据添加时间查询
        if add_time_gte:
            query = query.where(FastZdpUploadFileModel.add_time >= add_time_gte)
        if add_time_lte:
            query = query.where(FastZdpUploadFileModel.add_time <= add_time_lte)
        # 根据大小查询
        if size_gte:
            query = query.where(FastZdpUploadFileModel.size >= size_gte)
        if size_lte:
            query = query.where(FastZdpUploadFileModel.size <= size_lte)

        # 统计总数
        total_count = len(db.exec(query).all())

        # 分页
        query = query.offset((page - 1) * size).limit(size)
        # 执行查询
        results = db.exec(query).all()
        # 返回
        return {
            "count": total_count,
            "data": results,
        }

    @router.delete("/fastzdp_upload/{uid}/", summary="删除文件")
    def get_file(
            uid: int,
            db: Session = Depends(get_db),
    ):
        """
        根据ID删除文件
        """
        # 检查文件是否存在
        db_file = db.exec(select(FastZdpUploadFileModel).where(FastZdpUploadFileModel.id == uid)).first()
        if not db_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file is not exist")

        # 删除文件
        try:
            os.remove(db_file.path)
        except Exception as e:
            print(e)

        # 删除表记录
        db.delete(db_file)
        db.commit()

        return {"filename": db_file.nickname}

    @router.put("/fastzdp_upload/{uid}/{name}/", summary="修改文件名称")
    def update_name(
            uid: int,
            name: str,
            db: Session = Depends(get_db),
    ):
        """
        根据ID修改文件名
        """
        # 检查文件是否存在
        db_file = db.exec(select(FastZdpUploadFileModel).where(FastZdpUploadFileModel.id == uid)).first()
        if not db_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file is not exist")

        # 修改
        old_name = db_file.nickname
        if name:
            db_file.nickname = name
        db.add(db_file)
        db.commit()

        return {
            "old_name": old_name,
            "new_name": name,
        }

    return router
