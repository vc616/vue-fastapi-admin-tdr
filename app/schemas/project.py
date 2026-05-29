from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(..., description="项目名称")
    path: str = Field(..., description="路径标识")
    icon: str | None = Field("carbon:device", description="图标")
    order: int = Field(0, description="排序")
    datasource_id: int | None = Field(None, description="关联数据源ID")
    table_name: str | None = Field(None, description="数据表名")
    grafana_url: str | None = Field(None, description="Grafana dashboard URL")
    grafana_panel_url: str | None = Field(None, description="Grafana panel URL")
    model_3d_url: str | None = Field(None, description="3D模型文件路径")
    # 3D视图参数
    camera_position: list = Field([0, 2, 5], description="相机位置 [x, y, z]")
    model_target: list = Field([0, 0, 0], description="旋转轴心 [x, y, z]")
    model_rotation: list = Field([0, 0, 0], description="模型初始旋转 [rx, ry, rz]")
    auto_rotate: bool = Field(False, description="是否自动旋转")
    auto_rotate_speed: float = Field(1.0, description="自动旋转速度")
    is_hidden: bool = Field(False, description="是否隐藏")
    keepalive: bool = Field(True, description="存活")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    id: int


class ProjectOut(ProjectBase):
    id: int
