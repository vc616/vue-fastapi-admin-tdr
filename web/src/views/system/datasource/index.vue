<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import { NButton, NForm, NFormItem, NInput, NInputNumber, NPopconfirm } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import { renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'

defineOptions({ name: '数据源管理' })

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
  name: '数据源',
  initForm: { name: 'grafana', host: '192.168.6.8', port: 3306, username: 'root', password: 'grafana123', database: 'grafana' },
  doCreate: api.createDataSource,
  doUpdate: api.updateDataSource,
  doDelete: api.deleteDataSource,
  refresh: () => $table.value?.handleSearch(),
})

const datasourceRules = {
  name: [
    {
      required: true,
      message: '请输入数据源名称',
      trigger: ['input', 'blur', 'change'],
    },
  ],
  host: [
    {
      required: true,
      message: '请输入数据库地址',
      trigger: ['input', 'blur', 'change'],
    },
  ],
  port: [],
  username: [
    {
      required: true,
      message: '请输入用户名',
      trigger: ['input', 'blur', 'change'],
    },
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: ['input', 'blur', 'change'],
    },
  ],
  database: [
    {
      required: true,
      message: '请输入数据库名称',
      trigger: ['input', 'blur', 'change'],
    },
  ],
}

const columns = [
  {
    title: '数据源名称',
    key: 'name',
    width: 'auto',
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '数据库地址',
    key: 'host',
    width: 'auto',
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '端口',
    key: 'port',
    width: 100,
    align: 'center',
  },
  {
    title: '用户名',
    key: 'username',
    width: 'auto',
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '数据库名称',
    key: 'database',
    width: 'auto',
    align: 'center',
    ellipsis: { tooltip: true },
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
          [[vPermission, 'post/api/v1/datasource/update']]
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
                [[vPermission, 'delete/api/v1/datasource/delete']]
              ),
            default: () => h('div', {}, '确定删除该数据源吗?'),
          }
        ),
      ]
    },
  },
]

onMounted(() => {
  $table.value?.handleSearch()
})
</script>

<template>
  <!-- 业务页面 -->
  <CommonPage show-footer title="数据源列表">
    <template #action>
      <div>
        <NButton
          v-permission="'post/api/v1/datasource/create'"
          class="float-right mr-15"
          type="primary"
          @click="handleAdd"
        >
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建数据源
        </NButton>
      </div>
    </template>
    <!-- 表格 -->
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getDataSourceList"
    >
      <template #queryBar>
        <QueryBarItem label="数据源名称" :label-width="80">
          <NInput
            v-model:value="queryItems.name"
            clearable
            type="text"
            placeholder="请输入数据源名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <!-- 新增/编辑 弹窗 -->
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
        :label-width="90"
        :model="modalForm"
        :rules="datasourceRules"
      >
        <NFormItem label="数据源名称" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入数据源名称" />
        </NFormItem>
        <NFormItem label="数据库地址" path="host">
          <NInput v-model:value="modalForm.host" clearable placeholder="请输入数据库地址" />
        </NFormItem>
        <NFormItem label="端口" path="port">
          <NInputNumber v-model:value="modalForm.port" min="1" max="65535" placeholder="请输入端口" />
        </NFormItem>
        <NFormItem label="用户名" path="username">
          <NInput v-model:value="modalForm.username" clearable placeholder="请输入用户名" />
        </NFormItem>
        <NFormItem label="密码" path="password">
          <NInput v-model:value="modalForm.password" type="password" clearable placeholder="请输入密码" />
        </NFormItem>
        <NFormItem label="数据库名称" path="database">
          <NInput v-model:value="modalForm.database" clearable placeholder="请输入数据库名称" />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>