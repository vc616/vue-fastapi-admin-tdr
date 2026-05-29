from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth
from app.models.admin import Api, Menu, Role, User
from app.schemas.base import Fail, Success
from app.schemas.login import *
from app.schemas.users import SendVerifyCode, ResetPassword, UpdatePassword
from app.settings import settings
from app.utils.email import generate_verify_code, send_verify_code_email
from app.utils.jwt_utils import create_access_token
from app.utils.password import get_password_hash, verify_password
from app.utils.verify_code import verify_code_store

router = APIRouter()


@router.post("/access_token", summary="获取token")
async def login_access_token(credentials: CredentialsSchema):
    user: User = await user_controller.authenticate(credentials)
    await user_controller.update_last_login(user.id)
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires

    data = JWTOut(
        access_token=create_access_token(
            data=JWTPayload(
                user_id=user.id,
                username=user.username,
                is_superuser=user.is_superuser,
                exp=expire,
            )
        ),
        username=user.username,
    )
    return Success(data=data.model_dump())


@router.get("/userinfo", summary="查看用户信息", dependencies=[DependAuth])
async def get_userinfo():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    data = await user_obj.to_dict(exclude_fields=["password"])
    data["avatar"] = f"https://ui-avatars.com/api/?name={user_obj.username}&background=1a1a2e&color=60a5fa&size=128&font-size=0.4&bold=true"
    return Success(data=data)


@router.get("/usermenu", summary="查看用户菜单", dependencies=[DependAuth])
async def get_user_menu():
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    menus: list[Menu] = []
    if user_obj.is_superuser:
        menus = await Menu.all()
    else:
        role_objs: list[Role] = await user_obj.roles
        for role_obj in role_objs:
            menu = await role_obj.menus
            menus.extend(menu)
        menus = list(set(menus))

    async def build_menu_tree(menu_list: list[Menu], parent_id: int) -> list:
        result = []
        for menu in menu_list:
            if menu.parent_id == parent_id:
                menu_dict = await menu.to_dict()
                menu_dict["children"] = await build_menu_tree(menu_list, menu.id)
                result.append(menu_dict)
        return result

    return Success(data=await build_menu_tree(menus, 0))


@router.get("/userapi", summary="查看用户API", dependencies=[DependAuth])
async def get_user_api():
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    if user_obj.is_superuser:
        api_objs: list[Api] = await Api.all()
        apis = [api.method.lower() + api.path for api in api_objs]
        return Success(data=apis)
    role_objs: list[Role] = await user_obj.roles
    apis = []
    for role_obj in role_objs:
        api_objs: list[Api] = await role_obj.apis
        apis.extend([api.method.lower() + api.path for api in api_objs])
    apis = list(set(apis))
    return Success(data=apis)


@router.post("/update_password", summary="修改密码", dependencies=[DependAuth])
async def update_user_password(req_in: UpdatePassword):
    user_id = CTX_USER_ID.get()
    user = await user_controller.get(user_id)
    verified = verify_password(req_in.old_password, user.password)
    if not verified:
        return Fail(msg="旧密码验证错误！")
    user.password = get_password_hash(req_in.new_password)
    await user.save()
    return Success(msg="修改成功")


@router.post("/send_verify_code", summary="发送验证码")
async def send_verify_code(req_in: SendVerifyCode):
    user = await User.filter(username=req_in.email).first()
    if not user:
        return Fail(msg="该用户名不存在")

    if not user.email:
        return Fail(msg="该用户未绑定邮箱，请联系管理员")

    code = generate_verify_code()
    verify_code_store.set(user.email, code, settings.VERIFY_CODE_EXPIRE_MINUTES * 60)

    if not settings.EMAIL_USERNAME or not settings.EMAIL_PASSWORD:
        return Fail(msg="邮件服务未配置")

    success = send_verify_code_email(user.email, code)
    if not success:
        return Fail(msg="发送验证码失败")

    return Success(msg="验证码已发送")


@router.post("/reset_password", summary="重置密码")
async def reset_password(req_in: ResetPassword):
    user = await User.filter(username=req_in.email).first()
    if not user:
        return Fail(msg="该用户名不存在")

    if not user.email:
        return Fail(msg="该用户未绑定邮箱，请联系管理员")

    if not verify_code_store.verify(user.email, req_in.code):
        return Fail(msg="验证码错误或已过期")

    user.password = get_password_hash(req_in.new_password)
    await user.save()
    return Success(msg="密码重置成功")
