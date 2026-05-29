from fastapi import APIRouter, Body, HTTPException, Query, UploadFile, File
import os
import uuid
from pathlib import Path

from app.controllers.project import project_controller
from app.models.admin import Menu
from app.schemas import Fail, Success, SuccessExtra
from app.schemas.project import ProjectCreate, ProjectUpdate

router = APIRouter()


async def get_equipment_menu_id() -> int:
    """获取设备管理目录的菜单ID"""
    menu = await Menu.filter(path="/equipment").first()
    if not menu:
        raise HTTPException(status_code=404, detail="设备管理菜单不存在")
    return menu.id


@router.get("/list", summary="查看项目列表")
async def list_project(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="项目名称"),
):
    from tortoise.expressions import Q
    q = Q()
    if name:
        q &= Q(name__contains=name)
    total, objs = await project_controller.list(page=page, page_size=page_size, search=q)
    data = [await obj.to_dict() for obj in objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get/{project_id}", summary="查看项目")
async def get_project(project_id: int):
    obj = await project_controller.get(id=project_id)
    if not obj:
        return Fail(msg="项目不存在")
    return Success(data=await obj.to_dict())


@router.get("/get_by_path/{path}", summary="根据路径查看项目")
async def get_project_by_path(path: str):
    obj = await project_controller.model.filter(path=path).first()
    if not obj:
        return Fail(msg="项目不存在")
    return Success(data=await obj.to_dict())


@router.post("/create", summary="创建项目")
async def create_project(project_in: ProjectCreate):
    try:
        equipment_menu_id = await get_equipment_menu_id()
    except HTTPException:
        # 如果设备管理菜单不存在，先创建它
        equipment_menu = await Menu.create(
            menu_type="catalog",
            name="设备管理",
            path="/equipment",
            order=2,
            parent_id=0,
            icon="carbon:devices",
            is_hidden=False,
            component="Layout",
            keepalive=False,
        )
        equipment_menu_id = equipment_menu.id

    project = await project_controller.create_with_menu(project_in, equipment_menu_id)
    return Success(msg="创建成功", data=await project.to_dict())


@router.post("/update", summary="更新项目")
async def update_project(project_in: ProjectUpdate):
    old_project = await project_controller.get(id=project_in.id)
    if not old_project:
        return Fail(msg="项目不存在")

    project = await project_controller.update(id=project_in.id, obj_in=project_in)

    # 更新对应的菜单
    await Menu.filter(path=old_project.path).update(
        name=project.name,
        path=project.path,
        icon=project.icon or "carbon:device",
        order=project.order,
        is_hidden=project.is_hidden,
    )

    return Success(msg="更新成功", data=await project.to_dict())


@router.delete("/delete/{project_id}", summary="删除项目")
async def delete_project(project_id: int):
    success = await project_controller.delete_with_menu(project_id)
    if not success:
        return Fail(msg="项目不存在")
    return Success(msg="删除成功")


@router.post("/upload_model", summary="上传3D模型文件")
async def upload_model(file: UploadFile = File(...), project_path: str = Query(None, description="项目路径")):
    """上传3D模型文件（.glb/.gltf）"""
    from app.settings import settings

    # 验证文件类型
    allowed_extensions = {'.glb', '.gltf'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        return Fail(msg=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}")

    # 保留原文件名
    original_filename = Path(file.filename).name
    # 保存到项目对应的设备文件夹（public目录下以便可访问）
    upload_dir = Path(settings.BASE_DIR) / "web" / "public" / "models" / project_path if project_path else Path(settings.BASE_DIR) / "web" / "public" / "models"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / original_filename

    # 如果文件已存在，先删除
    if file_path.exists():
        file_path.unlink()

    # 保存文件
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 验证文件是否写入成功
    if not file_path.exists():
        raise HTTPException(status_code=500, detail="文件保存失败")

    file_size = file_path.stat().st_size
    if file_size == 0:
        file_path.unlink()
        raise HTTPException(status_code=500, detail="文件为空")

    # 返回访问路径
    model_url = f"/models/{project_path}/{original_filename}" if project_path else f"/models/{original_filename}"

    # 如果提供了项目路径，更新项目的 model_3d_url
    if project_path:
        from app.models.admin import Project
        project = await Project.filter(path=project_path).first()
        if project:
            await project.update_from_dict({"model_3d_url": model_url})
            await project.save()

    return Success(data={"url": model_url, "filename": original_filename})


@router.get("/tables", summary="获取项目可用的数据表")
async def get_project_tables(datasource_id: int = Query(..., description="数据源ID")):
    """获取指定数据源的所有表名"""
    from app.models.admin import DataSource
    import pymysql

    ds = await DataSource.filter(id=datasource_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail=f"数据源不存在")

    connection = None
    try:
        connection = pymysql.connect(
            host=ds.host,
            port=ds.port,
            user=ds.username,
            password=ds.password,
            database=ds.database,
            connect_timeout=5
        )
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
        return Success(data=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
    finally:
        if connection:
            connection.close()


@router.get("/columns", summary="获取表字段列表")
async def get_project_columns(
    datasource_id: int = Query(..., description="数据源ID"),
    table_name: str = Query(..., description="表名"),
):
    """获取指定表的字段列表"""
    from app.models.admin import DataSource
    import pymysql

    ds = await DataSource.filter(id=datasource_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail=f"数据源不存在")

    connection = None
    try:
        connection = pymysql.connect(
            host=ds.host,
            port=ds.port,
            user=ds.username,
            password=ds.password,
            database=ds.database,
        )
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
            columns = [
                {"field": row[0], "type": row[1], "comment": row[8] or ""}
                for row in cursor.fetchall()
            ]
        return Success(data=columns)
    finally:
        if connection:
            connection.close()


@router.get("/export", summary="数据导出")
async def export_project_data(
    datasource_id: int = Query(..., description="数据源ID"),
    table_name: str = Query(..., description="表名"),
    columns: str = Query("", description="导出字段，逗号分隔"),
    start_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间"),
):
    """从指定数据源导出数据为Excel格式"""
    from app.models.admin import DataSource
    import pymysql
    import io
    import xlsxwriter
    from datetime import datetime as dt

    ds = await DataSource.filter(id=datasource_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail=f"数据源不存在")

    connection = None
    try:
        connection = pymysql.connect(
            host=ds.host,
            port=ds.port,
            user=ds.username,
            password=ds.password,
            database=ds.database,
            connect_timeout=5
        )
        with connection.cursor() as cursor:
            col_str = columns if columns else "*"
            where_clause = ""
            params = []
            if start_time:
                where_clause += " AND time >= %s"
                params.append(start_time)
            if end_time:
                where_clause += " AND time <= %s"
                params.append(end_time)

            sql = f"SELECT {col_str} FROM {table_name} WHERE 1=1{where_clause}"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet(table_name)
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#CCCCCC"})
        date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})
        for col_idx, col_name in enumerate(cols):
            sheet.write(0, col_idx, col_name, header_fmt)
        for row_idx, row in enumerate(rows, start=1):
            for col_idx, value in enumerate(row):
                if isinstance(value, dt):
                    sheet.write_datetime(row_idx, col_idx, value, date_fmt)
                else:
                    sheet.write(row_idx, col_idx, value)
        workbook.close()
        output.seek(0)

        from fastapi.responses import StreamingResponse

        filename = f"{table_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    finally:
        if connection:
            connection.close()
