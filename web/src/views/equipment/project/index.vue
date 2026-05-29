<script setup>
import dayjs from 'dayjs'
import api from '@/api'

defineOptions({ name: '设备主页' })

const route = useRoute()
const iframeRef = ref(null)
const isFullscreen = ref(false)
const exporting = ref(false)
const loadingColumns = ref(false)

const projectConfig = ref(null)
const loading = ref(true)
const error = ref(null)

// 从 grafana_url 字段提取真正的 URL（支持 iframe HTML 或纯 URL）
const grafanaPidUrl = computed(() => {
  if (!projectConfig.value?.grafana_url) return null
  const url = projectConfig.value.grafana_url
  const match = url.match(/src=["']([^"']+)["']/)
  return match ? match[1] : url
})

const columnOptions = ref([])
const allFields = computed(() => columnOptions.value.map((col) => col.field))
const isAllSelected = computed(
  () => columnOptions.value.length > 0 && exportForm.value.selectedFields.length === columnOptions.value.length
)
const isIndeterminate = computed(
  () => exportForm.value.selectedFields.length > 0 && !isAllSelected.value
)

const defaultForm = {
  selectedFields: [],
  startTime: null,
  endTime: null,
}

const exportForm = ref({ ...defaultForm })

onMounted(async () => {
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })

  const projectPath = route.query.path || new URLSearchParams(window.location.search).get('path') || ''
  if (!projectPath) {
    error.value = '缺少项目路径参数'
    loading.value = false
    return
  }

  try {
    const res = await api.getProjectByPath(projectPath)
    if (res.code === 200 && res.data) {
      projectConfig.value = res.data
      if (res.data.datasource_id && res.data.table_name) {
        await loadColumns(res.data.table_name)
      }
    } else {
      error.value = '项目不存在'
    }
  } catch (e) {
    console.error('加载项目配置失败', e)
    error.value = '加载项目配置失败'
  } finally {
    loading.value = false
  }
})

async function loadColumns(tableName) {
  loadingColumns.value = true
  try {
    const res = await api.getProjectColumns({
      datasource_id: projectConfig.value.datasource_id,
      table_name: tableName,
    })
    columnOptions.value = res.data || []
    exportForm.value.selectedFields = allFields.value
  } catch (e) {
    console.error('获取字段列表失败', e)
  } finally {
    loadingColumns.value = false
  }
}

function toggleSelectAll(value) {
  exportForm.value.selectedFields = value ? [...allFields.value] : []
}

function reverseSelection() {
  exportForm.value.selectedFields = allFields.value.filter(
    (field) => !exportForm.value.selectedFields.includes(field)
  )
}

function handleReset() {
  exportForm.value.selectedFields = []
  exportForm.value.startTime = null
  exportForm.value.endTime = null
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    iframeRef.value?.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

async function handleExport() {
  if (!projectConfig.value?.datasource_id || !projectConfig.value?.table_name) {
    $message.warning('项目未配置数据源和数据表')
    return
  }

  exporting.value = true
  try {
    const params = {
      datasource_id: projectConfig.value.datasource_id,
      table_name: projectConfig.value.table_name,
      columns: exportForm.value.selectedFields.join(','),
    }
    if (exportForm.value.startTime) {
      params.start_time = dayjs(exportForm.value.startTime).format('YYYY-MM-DD HH:mm:ss')
    }
    if (exportForm.value.endTime) {
      params.end_time = dayjs(exportForm.value.endTime).format('YYYY-MM-DD HH:mm:ss')
    }

    const blob = await api.exportProjectData(params)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${projectConfig.value.table_name}_${dayjs().format('YYYYMMDDHHmmss')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    $message.success('导出成功')
  } catch (e) {
    console.error('导出失败', e)
    $message.error('导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <AppPage>
    <template v-if="loading">
      <div class="flex items-center justify-center h-200">
        <n-spin size="large" />
        <span class="ml-10">加载中...</span>
      </div>
    </template>

    <template v-else-if="error">
      <n-result status="404" title="加载失败" :description="error">
        <template #footer>
          <n-button @click="$router.go(-1)">返回上一页</n-button>
        </template>
      </n-result>
    </template>

    <template v-else-if="projectConfig">
      <n-tabs type="line" animated>
        <n-tab-pane name="preview" tab="设备预览">
          <div class="relative">
            <n-button class="absolute right-4 top-4 z-10" @click="toggleFullscreen">
              {{ isFullscreen ? '退出全屏' : '全屏' }}
            </n-button>
            <iframe
              v-if="projectConfig.grafana_panel_url"
              ref="iframeRef"
              :src="projectConfig.grafana_panel_url"
              width="100%"
              height="1000px"
              frameborder="0"
            />
            <n-empty v-else description="该项目未配置Grafana面板URL" />
          </div>
        </n-tab-pane>

        <n-tab-pane name="pid" tab="PID">
          <div class="pid-container">
            <div v-if="grafanaPidUrl" class="pid-iframe-wrapper">
              <iframe
                :src="grafanaPidUrl"
                width="100%"
                height="100%"
                frameborder="0"
                class="pid-iframe"
              />
            </div>
            <n-empty v-else description="该项目未配置 Grafana PID" />
          </div>
        </n-tab-pane>

        <n-tab-pane name="dashboard" tab="仪表板">
          <div class="relative">
            <n-button class="absolute right-4 top-4 z-10" @click="toggleFullscreen">
              {{ isFullscreen ? '退出全屏' : '全屏' }}
            </n-button>
            <iframe
              v-if="projectConfig.grafana_url"
              ref="iframeRef"
              :src="projectConfig.grafana_url"
              width="100%"
              height="1000px"
              frameborder="0"
            />
            <n-empty v-else description="该项目未配置Grafana Dashboard URL" />
          </div>
        </n-tab-pane>

        <n-tab-pane name="export" tab="数据导出">
          <div class="export-container">
            <n-card class="export-card" :bordered="false">
              <template #header>数据导出工具</template>

              <div class="step-item">
                <div class="step-header">
                  <span class="step-num">1</span>
                  <span class="step-title">时间范围</span>
                </div>
                <div class="step-content">
                  <n-grid :cols="2" :x-gap="12">
                    <n-gi>
                      <n-date-picker
                        v-model:value="exportForm.startTime"
                        type="datetime"
                        clearable
                        placeholder="开始时间"
                        style="width: 100%"
                      />
                    </n-gi>
                    <n-gi>
                      <n-date-picker
                        v-model:value="exportForm.endTime"
                        type="datetime"
                        clearable
                        placeholder="结束时间"
                        style="width: 100%"
                      />
                    </n-gi>
                  </n-grid>
                </div>
              </div>

              <div class="step-item">
                <div class="step-header">
                  <span class="step-num">2</span>
                  <span class="step-title">选择导出字段</span>
                </div>
                <div class="step-content">
                  <div v-if="!projectConfig.table_name" class="empty-tip">
                    <span>该项目未配置数据表</span>
                  </div>
                  <div v-else-if="loadingColumns" class="loading-tip">
                    <n-spin size="small" />
                    <span>加载字段中...</span>
                  </div>
                  <div v-else class="field-list">
                    <div class="field-actions">
                      <n-checkbox
                        :checked="isAllSelected"
                        :indeterminate="isIndeterminate"
                        @update:checked="toggleSelectAll"
                      >
                        全选
                      </n-checkbox>
                      <n-button text size="small" @click="reverseSelection">反选</n-button>
                    </div>
                    <n-checkbox-group v-model:value="exportForm.selectedFields">
                      <n-space item-style="display: flex;" vertical>
                        <n-checkbox
                          v-for="col in columnOptions"
                          :key="col.field"
                          :value="col.field"
                          :label="col.comment || col.field"
                        />
                      </n-space>
                    </n-checkbox-group>
                  </div>
                </div>
              </div>

              <div class="action-bar">
                <div class="export-info">
                  <span v-if="exportForm.selectedFields.length">
                    已选择 {{ exportForm.selectedFields.length }} 个字段
                  </span>
                </div>
                <n-space>
                  <n-button @click="handleReset">重置</n-button>
                  <n-button type="primary" :loading="exporting" @click="handleExport">
                    导出 Excel
                  </n-button>
                </n-space>
              </div>
            </n-card>

            <div class="format-info">
              <span>输出格式：Excel 2007+ (.xlsx)</span>
            </div>
          </div>
        </n-tab-pane>
      </n-tabs>
    </template>
  </AppPage>
</template>

<style scoped>
.export-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.export-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.step-item {
  background: #fafafa;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  color: #333;
}

.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #18a058;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.step-title {
  font-size: 15px;
  font-weight: 500;
}

.step-content {
  padding-left: 34px;
}

.empty-tip,
.loading-tip {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #999;
  padding: 20px 0;
}

.field-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 12px;
}

.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.export-info {
  color: #666;
  font-size: 13px;
}

.format-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 16px;
  color: #999;
  font-size: 12px;
}

.pid-container {
  width: 100%;
  height: 800px;
}

.pid-iframe-wrapper {
  width: 100%;
  height: 100%;
}

.pid-iframe {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
