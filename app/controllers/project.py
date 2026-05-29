from app.core.crud import CRUDBase
from app.models.admin import Menu, Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.utils.component_generator import create_project_component, delete_project_component


class ProjectController(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def __init__(self):
        super().__init__(model=Project)

    async def create_with_menu(self, obj_in: ProjectCreate, equipment_menu_id: int) -> Project:
        """创建项目并自动创建对应的菜单和前端组件"""
        project = await self.create(obj_in)

        # 创建设备专属组件文件
        component_path = create_project_component(project.path)

        # 创建设备菜单
        await Menu.create(
            name=project.name,
            path=project.path,
            icon=project.icon or "carbon:device",
            order=project.order,
            parent_id=equipment_menu_id,
            is_hidden=project.is_hidden,
            component=component_path,
            keepalive=project.keepalive,
            menu_type="menu",
            redirect=f"/{component_path}",
        )
        return project

    async def delete_with_menu(self, id: int) -> bool:
        """删除项目并自动删除对应的菜单和前端组件"""
        project = await self.get(id=id)
        if not project:
            return False

        project_path = project.path
        # 删除对应的菜单
        await Menu.filter(path=project_path).delete()
        # 删除项目
        await self.remove(id=id)
        # 删除前端组件文件
        delete_project_component(project_path)
        return True


project_controller = ProjectController()
