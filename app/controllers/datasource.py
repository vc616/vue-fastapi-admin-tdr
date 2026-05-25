from app.core.crud import CRUDBase
from app.models.admin import DataSource
from app.schemas.datasource import DataSourceCreate, DataSourceUpdate


class DataSourceController(CRUDBase[DataSource, DataSourceCreate, DataSourceUpdate]):
    def __init__(self):
        super().__init__(model=DataSource)


datasource_controller = DataSourceController()