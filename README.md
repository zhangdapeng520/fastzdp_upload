# fastzdp_upload

专为FastAPI打造的处理文件上传下载的框架

Github项目开源地址：https://github.com/zhangdapeng520/fastzdp_upload

## 特性

- 1、伪代码开发
- 2、自动拥有上传文件的接口
- 3、自动拥有下载文件的接口
- 4、自动拥有搜索文件的接口
- 5、自动拥有修改文件名的接口
- 6、自动拥有删除文件的接口

## 使用教程

### 安装

```bash
pip install fastzdp_upload
```

### 快速入门

启动下面的服务以后，浏览器访问接口文档：http://127.0.0.1:8888/docs

```python
import fastzdp_upload
from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session

# 创建数据库引擎
sqlite_url = "mysql+pymysql://root:root@127.0.0.1:3306/fastzdp_upload?charset=utf8mb4"
engine = create_engine(sqlite_url, echo=True)

# 确保表存在
SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

app.include_router(fastzdp_upload.get_router(get_db))

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8888)
```

## 版本历史

### v0.1.3

- 基本功能实现，代码迁移至Github

### v0.1.4

- 解决和fastzdp-api依赖冲突的问题
