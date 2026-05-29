<script setup>
import { h, onMounted, ref, computed, resolveDirective, withDirectives } from 'vue'
import { NButton, NForm, NFormItem, NInput, NInputNumber, NPopconfirm, NSelect, NSpace, NSwitch } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import { renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'

defineOptions({ name: '项目管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')

const {
  modalVisible,
  modalTitle,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '项目',
  initForm: {
    name: '',
    path: '',
    icon: 'carbon:device',
    order: 0,
    datasource_id: null,
    table_name: null,
    grafana_url: null,
    grafana_panel_url: null,
    model_3d_url: null,
    camera_position: [0, 2, 5],
    model_target: [0, 0, 0],
    model_rotation: [0, 0, 0],
    auto_rotate: false,
    auto_rotate_speed: 1.0,
    is_hidden: false,
    keepalive: true,
  },
  doCreate: async (data) => {
    // 自动生成路径标识
    if (!data.path && data.name) {
      data.path = generatePath(data.name)
    }
    // 如果排序值为空，获取最大排序值+1
    if (data.order === undefined || data.order === null || data.order === 0) {
      data.order = await getDefaultOrder()
    }
    return api.createProject(data)
  },
  doUpdate: api.updateProject,
  doDelete: api.deleteProject,
  refresh: () => $table.value?.handleSearch(),
})

// 排序默认值：获取当前最大排序值+1
async function getDefaultOrder() {
  try {
    const res = await api.getProjectList({ page: 1, page_size: 1000 })
    if (res.data && res.data.length > 0) {
      const maxOrder = Math.max(...res.data.map((p) => p.order || 0))
      return maxOrder + 1
    }
  } catch (e) {
    console.error('获取排序值失败', e)
  }
  return 0
}

// 生成路径标识（基于项目名称）
function generatePath(name) {
  if (!name) return ''
  return name
    .toLowerCase()
    .replace(/[^a-z0-9一-龥]/g, '')
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/\s+/g, '_')
}

const datasourceOptions = ref([])
const tableOptions = ref([])
const loadingTables = ref(false)

async function loadDatasources() {
  try {
    const res = await api.getDataSourceList({ page: 1, page_size: 100 })
    datasourceOptions.value = (res.data || []).map((item) => ({
      label: item.name,
      value: item.id,
    }))
  } catch (e) {
    console.error('获取数据源列表失败', e)
  }
}

async function loadTables(datasourceId) {
  if (!datasourceId) {
    tableOptions.value = []
    return
  }
  loadingTables.value = true
  try {
    const res = await api.getProjectTables({ datasource_id: datasourceId })
    tableOptions.value = (res.data || []).map((name) => ({
      label: name,
      value: name,
    }))
  } catch (e) {
    console.error('获取表列表失败', e)
  } finally {
    loadingTables.value = false
  }
}

function handleDatasourceChange(value) {
  modalForm.table_name = null
  tableOptions.value = []
  if (value) {
    loadTables(value)
  }
}

// 上传3D模型
const uploadingModel = ref(false)
const fileInputRef = ref(null)

function triggerFileUpload() {
  fileInputRef.value?.click()
}

async function handleFileSelected(event) {
  const target = event.target
  const file = target.files?.[0]
  if (!file) return

  uploadingModel.value = true
  try {
    const projectPath = modalForm.path || null
    const res = await api.uploadProjectModel(file, projectPath)
    if (res.code === 200 && res.data?.url) {
      modalForm.model_3d_url = res.data.url
      $message.success('上传成功')
    } else {
      $message.error(res.msg || '上传失败')
    }
  } catch (e) {
    console.error('上传失败', e)
    $message.error('上传失败')
  } finally {
    uploadingModel.value = false
    // reset input
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  }
}

const projectRules = {
  name: [
    {
      required: true,
      message: '请输入项目名称',
      trigger: ['input', 'blur', 'change'],
    },
  ],
}

const columns = [
  {
    title: '项目名称',
    key: 'name',
    width: 'auto',
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '路径',
    key: 'path',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '数据源',
    key: 'datasource_id',
    width: 120,
    align: 'center',
    render(row) {
      const ds = datasourceOptions.value.find((d) => d.value === row.datasource_id)
      return ds ? ds.label : '-'
    },
  },
  {
    title: '数据表',
    key: 'table_name',
    width: 120,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: 'Grafana PID',
    key: 'grafana_url',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '3D模型',
    key: 'model_3d_url',
    width: 100,
    align: 'center',
    render(row) {
      return row.model_3d_url ? '已上传' : '-'
    },
  },
  {
    title: '排序',
    key: 'order',
    width: 80,
    align: 'center',
  },
  {
    title: '操作',
    key: 'actions',
    width: 'auto',
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              style: 'margin-left: 8px;',
              onClick: () => handleEdit(row),
            },
            {
              default: () => '编辑',
              icon: renderIcon('material-symbols:edit', { size: 16 }),
            }
          ),
          [[vPermission, 'post/api/v1/project/update']]
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDelete({ id: row.id }, false),
            onNegativeClick: () => {},
          },
          {
            trigger: () =>
              withDirectives(
                h(
                  NButton,
                  {
                    size: 'small',
                    type: 'error',
                    style: 'margin-left: 8px;',
                  },
                  {
                    default: () => '删除',
                    icon: renderIcon('material-symbols:delete-outline', { size: 16 }),
                  }
                ),
                [[vPermission, 'delete/api/v1/project/delete']]
              ),
            default: () => h('div', {}, '确定删除该项目吗？相关菜单也会被删除。'),
          }
        ),
      ]
    },
  },
]

onMounted(async () => {
  $table.value?.handleSearch()
  await loadDatasources()
})
</script>

<template>
  <CommonPage show-footer title="项目列表">
    <template #action>
      <div>
        <NButton
          v-permission="'post/api/v1/project/create'"
          class="float-right mr-15"
          type="primary"
          @click="handleAdd"
        >
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建项目
        </NButton>
      </div>
    </template>
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getProjectList"
    >
      <template #queryBar>
        <QueryBarItem label="项目名称" :label-width="80">
          <NInput
            v-model:value="queryItems.name"
            clearable
            type="text"
            placeholder="请输入项目名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <NForm
        ref="modalFormRef"
        label-placement="left"
        label-align="left"
        :label-width="100"
        :model="modalForm"
        :rules="projectRules"
      >
        <NFormItem label="项目名称" path="name">
          <NInput
            v-model:value="modalForm.name"
            clearable
            placeholder="请输入项目名称"
          />
        </NFormItem>
        <NFormItem label="路径标识" path="path">
          <NInput
            v-model:value="modalForm.path"
            readonly
            placeholder="自动生成，无需填写"
          />
        </NFormItem>
        <NFormItem label="图标" path="icon">
          <NInput v-model:value="modalForm.icon" clearable placeholder="图标名称" />
        </NFormItem>
        <NFormItem label="排序" path="order">
          <NInputNumber v-model:value="modalForm.order" min="0" placeholder="留空则自动排序" />
        </NFormItem>
        <NFormItem label="数据源" path="datasource_id">
          <NSelect
            v-model:value="modalForm.datasource_id"
            :options="datasourceOptions"
            placeholder="请选择数据源"
            clearable
            @update:value="handleDatasourceChange"
          />
        </NFormItem>
        <NFormItem label="数据表" path="table_name">
          <NSelect
            v-model:value="modalForm.table_name"
            :options="tableOptions"
            :loading="loadingTables"
            :disabled="!modalForm.datasource_id"
            placeholder="请先选择数据源"
            clearable
          />
        </NFormItem>
        <NFormItem label="Grafana PID" path="grafana_url">
          <NInput
            v-model:value="modalForm.grafana_url"
            type="textarea"
            :rows="3"
            clearable
            placeholder="Grafana dashboard URL（支持长链接）"
          />
        </NFormItem>
        <NFormItem label="Grafana Panel URL" path="grafana_panel_url">
          <NInput
            v-model:value="modalForm.grafana_panel_url"
            type="textarea"
            :rows="3"
            clearable
            placeholder="Grafana panel URL（支持长链接）"
          />
        </NFormItem>
        <NFormItem label="3D模型" path="model_3d_url">
          <div class="model-upload">
            <input
              ref="fileInputRef"
              type="file"
              accept=".glb,.gltf"
              style="display: none"
              @change="handleFileSelected"
            />
            <NButton :loading="uploadingModel" size="small" @click="triggerFileUpload">
              上传模型
            </NButton>
            <span class="model-status">
              {{ modalForm.model_3d_url ? modalForm.model_3d_url.split('/').pop() : '未上传模型' }}
            </span>
          </div>
        </NFormItem>
        <NFormItem label="相机位置" path="camera_position">
          <NSpace>
            <NInputNumber v-model:value="modalForm.camera_position[0]" min="-100" max="100" placeholder="X" style="width: 80px" />
            <NInputNumber v-model:value="modalForm.camera_position[1]" min="-100" max="100" placeholder="Y" style="width: 80px" />
            <NInputNumber v-model:value="modalForm.camera_position[2]" min="-100" max="100" placeholder="Z" style="width: 80px" />
          </NSpace>
        </NFormItem>
        <NFormItem label="旋转轴心" path="model_target">
          <NSpace>
            <NInputNumber v-model:value="modalForm.model_target[0]" min="-100" max="100" placeholder="X" style="width: 80px" />
            <NInputNumber v-model:value="modalForm.model_target[1]" min="-100" max="100" placeholder="Y" style="width: 80px" />
            <NInputNumber v-model:value="modalForm.model_target[2]" min="-100" max="100" placeholder="Z" style="width: 80px" />
          </NSpace>
        </NFormItem>
        <NFormItem label="模型旋转" path="model_rotation">
          <NSpace>
            <NInputNumber v-model:value="modalForm.model_rotation[0]" min="-180" max="180" placeholder="X°" style="width: 80px" />
            <NInputNumber v-model:value="modalForm.model_rotation[1]" min="-180" max="180" placeholder="Y°" style="width: 80px" />
            <NInputNumber v-model:value="modalForm.model_rotation[2]" min="-180" max="180" placeholder="Z°" style="width: 80px" />
          </NSpace>
        </NFormItem>
        <NFormItem label="自动旋转" path="auto_rotate">
          <NSwitch v-model:value="modalForm.auto_rotate" />
        </NFormItem>
        <NFormItem v-if="modalForm.auto_rotate" label="旋转速度" path="auto_rotate_speed">
          <NInputNumber v-model:value="modalForm.auto_rotate_speed" min="0.1" max="10" step="0.1" />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<style scoped>
.model-upload {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-status {
  color: #666;
  font-size: 13px;
}
</style>
