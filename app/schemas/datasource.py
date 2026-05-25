from pydantic import BaseModel, Field


class DataSourceBase(BaseModel):
    name: str = Field("grafana", description="数据源名称")
    host: str = Field(..., description="数据库地址")
    port: int = Field(3306, description="端口")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    database: str = Field(..., description="数据库名称")


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(DataSourceBase):
    id: int


class DataSourceOut(DataSourceBase):
    id: int