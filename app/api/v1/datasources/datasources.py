from datetime import datetime
from typing import Optional

import pymysql
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from tortoise.expressions import Q

from app.controllers.datasource import datasource_controller
from app.schemas import Success, SuccessExtra
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate

router = APIRouter()


@router.get("/list", summary="查看数据源列表")
async def list_datasource(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="数据源名称"),
):
    q = Q()
    if name:
        q &= Q(name__contains=name)
    total, objs = await datasource_controller.list(page=page, page_size=page_size, search=q)
    data = [await obj.to_dict(exclude_fields=["password"]) for obj in objs]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看数据源")
async def get_datasource(
    id: int = Query(..., description="数据源ID"),
):
    obj = await datasource_controller.get(id=id)
    return Success(data=await obj.to_dict(exclude_fields=["password"]))


@router.post("/create", summary="创建数据源")
async def create_datasource(
    datasource_in: DataSourceCreate,
):
    await datasource_controller.create(obj_in=datasource_in)
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新数据源")
async def update_datasource(
    datasource_in: DataSourceUpdate,
):
    await datasource_controller.update(id=datasource_in.id, obj_in=datasource_in)
    return Success(msg="Update Successfully")


@router.delete("/delete", summary="删除数据源")
async def delete_datasource(
    id: int = Query(..., description="数据源ID"),
):
    await datasource_controller.remove(id=id)
    return Success(msg="Deleted Successfully")


@router.get("/tables", summary="获取数据源表列表")
async def get_tables(
    datasource_name: str = Query(..., description="数据源名称"),
):
    """获取指定数据源的所有表名"""
    q = Q(name=datasource_name)
    _, objs = await datasource_controller.list(page=1, page_size=1, search=q)
    if not objs:
        raise HTTPException(status_code=404, detail=f"数据源 '{datasource_name}' 不存在")
    ds = await objs[0].to_dict()

    connection = None
    try:
        connection = pymysql.connect(
            host=ds["host"],
            port=ds["port"],
            user=ds["username"],
            password=ds["password"],
            database=ds["database"],
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
async def get_columns(
    datasource_name: str = Query(..., description="数据源名称"),
    table_name: str = Query(..., description="表名"),
):
    """获取指定表的字段列表"""
    q = Q(name=datasource_name)
    _, objs = await datasource_controller.list(page=1, page_size=1, search=q)
    if not objs:
        raise HTTPException(status_code=404, detail=f"数据源 '{datasource_name}' 不存在")
    ds = await objs[0].to_dict()

    connection = None
    try:
        connection = pymysql.connect(
            host=ds["host"],
            port=ds["port"],
            user=ds["username"],
            password=ds["password"],
            database=ds["database"],
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
async def export_data(
    datasource_name: str = Query("grafana", description="数据源名称"),
    table_name: str = Query("juancheng", description="表名"),
    columns: str = Query("", description="导出字段，逗号分隔"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
):
    """从指定数据源导出数据为Excel格式"""
    try:
        # 获取数据源配置
        q = Q(name=datasource_name)
        _, objs = await datasource_controller.list(page=1, page_size=1, search=q)
        if not objs:
            raise HTTPException(status_code=404, detail=f"数据源 '{datasource_name}' 不存在")
        ds = await objs[0].to_dict()

        # 连接数据库
        connection = pymysql.connect(
            host=ds["host"],
            port=ds["port"],
            user=ds["username"],
            password=ds["password"],
            database=ds["database"],
            connect_timeout=5
        )
        try:
            with connection.cursor() as cursor:
                # 构建查询
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

            # 生成Excel
            import io
            import xlsxwriter
            from datetime import datetime as dt

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

            filename = f"{table_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"},
            )
        finally:
            connection.close()
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
