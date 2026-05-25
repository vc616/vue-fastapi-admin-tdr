from datetime import datetime, timedelta

from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.models.admin import Api, AuditLog, Dept, Menu, Role, User
from app.schemas import Success

router = APIRouter()


@router.get("/dashboard", summary="仪表盘汇总数据")
async def get_dashboard():
    """返回系统各模块的统计汇总数据"""
    total_users = await User.all().count()
    active_users = await User.filter(is_active=True).count()
    total_roles = await Role.all().count()
    total_menus = await Menu.all().count()
    total_apis = await Api.all().count()
    total_depts = await Dept.filter(is_deleted=False).count()

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_audit_count = await AuditLog.filter(created_at__gte=today).count()

    recent_audits = (
        await AuditLog.all()
        .order_by("-created_at")
        .limit(10)
        .values(
            "id",
            "username",
            "module",
            "summary",
            "method",
            "path",
            "status",
            "response_time",
            "created_at",
        )
    )
    for audit in recent_audits:
        if audit["created_at"]:
            audit["created_at"] = audit["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return Success(
        data={
            "total_users": total_users,
            "active_users": active_users,
            "total_roles": total_roles,
            "total_menus": total_menus,
            "total_apis": total_apis,
            "total_depts": total_depts,
            "today_audit_count": today_audit_count,
            "recent_audits": recent_audits,
        }
    )


@router.get("/chart", summary="图表数据")
async def get_chart_data(type: str = Query("weekly", description="图表类型，支持 weekly")):
    """返回近7天每日操作数量，用于折线图"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

    daily_counts = []
    for date_str in dates:
        date_start = datetime.strptime(date_str, "%Y-%m-%d")
        date_end = date_start + timedelta(days=1)
        count = await AuditLog.filter(
            created_at__gte=date_start, created_at__lt=date_end
        ).count()
        daily_counts.append({"date": date_str, "count": count})

    return Success(data={"type": type, "daily_counts": daily_counts})