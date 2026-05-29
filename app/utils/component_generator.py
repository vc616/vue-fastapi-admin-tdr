import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_COMPONENT = BASE_DIR / "web" / "src" / "views" / "equipment" / "_template" / "index.vue"
EQUIPMENT_VIEWS = BASE_DIR / "web" / "src" / "views" / "equipment"


def create_project_component(project_path: str) -> str:
    """创建设备对应的组件文件，返回组件路径"""
    dest_dir = EQUIPMENT_VIEWS / project_path
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "index.vue"
    shutil.copy(TEMPLATE_COMPONENT, dest_file)
    return f"/equipment/{project_path}"


def delete_project_component(project_path: str) -> None:
    """删除设备对应的组件文件"""
    dest_dir = EQUIPMENT_VIEWS / project_path
    if dest_dir.exists():
        shutil.rmtree(dest_dir)