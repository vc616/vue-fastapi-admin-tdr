import { request } from '@/utils'

export default {
  login: (data) => request.post('/base/access_token', data, { noNeedToken: true }),
  sendVerifyCode: (data) => request.post('/base/send_verify_code', data, { noNeedToken: true }),
  resetPassword: (data) => request.post('/base/reset_password', data, { noNeedToken: true }),
  getUserInfo: () => request.get('/base/userinfo'),
  getUserMenu: () => request.get('/base/usermenu'),
  getUserApi: () => request.get('/base/userapi'),
  // profile
  updatePassword: (data = {}) => request.post('/base/update_password', data),
  // users
  getUserList: (params = {}) => request.get('/user/list', { params }),
  getUserById: (params = {}) => request.get('/user/get', { params }),
  createUser: (data = {}) => request.post('/user/create', data),
  updateUser: (data = {}) => request.post('/user/update', data),
  deleteUser: (params = {}) => request.delete(`/user/delete`, { params }),
  // users - admin reset password (different endpoint)
  adminResetPassword: (data = {}) => request.post(`/user/reset_password`, data),
  // role
  getRoleList: (params = {}) => request.get('/role/list', { params }),
  createRole: (data = {}) => request.post('/role/create', data),
  updateRole: (data = {}) => request.post('/role/update', data),
  deleteRole: (params = {}) => request.delete('/role/delete', { params }),
  updateRoleAuthorized: (data = {}) => request.post('/role/authorized', data),
  getRoleAuthorized: (params = {}) => request.get('/role/authorized', { params }),
  // menus
  getMenus: (params = {}) => request.get('/menu/list', { params }),
  createMenu: (data = {}) => request.post('/menu/create', data),
  updateMenu: (data = {}) => request.post('/menu/update', data),
  deleteMenu: (params = {}) => request.delete('/menu/delete', { params }),
  // apis
  getApis: (params = {}) => request.get('/api/list', { params }),
  createApi: (data = {}) => request.post('/api/create', data),
  updateApi: (data = {}) => request.post('/api/update', data),
  deleteApi: (params = {}) => request.delete('/api/delete', { params }),
  refreshApi: (data = {}) => request.post('/api/refresh', data),
  // depts
  getDepts: (params = {}) => request.get('/dept/list', { params }),
  createDept: (data = {}) => request.post('/dept/create', data),
  updateDept: (data = {}) => request.post('/dept/update', data),
  deleteDept: (params = {}) => request.delete('/dept/delete', { params }),
  // auditlog
  getAuditLogList: (params = {}) => request.get('/auditlog/list', { params }),
  // datasource
  getDataSourceList: (params = {}) => request.get('/datasource/list', { params }),
  getDataSource: (params = {}) => request.get('/datasource/get', { params }),
  createDataSource: (data = {}) => request.post('/datasource/create', data),
  updateDataSource: (data = {}) => request.post('/datasource/update', data),
  deleteDataSource: (params = {}) => request.delete('/datasource/delete', { params }),
  exportData: (params = {}) => request.get('/datasource/export', { params, responseType: 'blob' }),
  getDataSourceTables: (params = {}) => request.get('/datasource/tables', { params }),
  getDataSourceColumns: (params = {}) => request.get('/datasource/columns', { params }),
  getDataSourceConfig: (configKey) => request.get(`/datasource/config/${configKey}`, { noNeedToken: true }),
  saveDataSourceConfig: (configKey, data) => request.post(`/datasource/config/${configKey}`, data, { noNeedToken: true }),
  // statistics
  getStatisticsDashboard: (params = {}) => request.get('/statistics/dashboard', { params }),
  getStatisticsChart: (params = {}) => request.get('/statistics/chart', { params }),
  // project
  getProjectList: (params = {}) => request.get('/project/list', { params }),
  getProject: (params = {}) => request.get('/project/get', { params }),
  getProjectByPath: (path) => request.get(`/project/get_by_path/${path}`),
  createProject: (data = {}) => request.post('/project/create', data),
  updateProject: (data = {}) => request.post('/project/update', data),
  deleteProject: (params = {}) => request.delete(`/project/delete/${params.id}`, { params }),
  getProjectTables: (params = {}) => request.get('/project/tables', { params }),
  getProjectColumns: (params = {}) => request.get('/project/columns', { params }),
  exportProjectData: (params = {}) => request.get('/project/export', { params, responseType: 'blob' }),
  uploadProjectModel: (file, projectPath = null) => {
    const formData = new FormData()
    formData.append('file', file)
    const url = projectPath ? `/project/upload_model?project_path=${encodeURIComponent(projectPath)}` : '/project/upload_model'
    return request.post(url, formData, { noNeedToken: true })
  },
}
