<template>
  <AppPage>
    <n-tabs type="line" animated>
      <n-tab-pane name="preview" tab="设备预览">
        <div ref="preview3DRef" class="preview-3d">
          <div class="preview-header">
            <n-button class="fullscreen-btn" @click="toggleFullscreenPreview">
              {{ isFullscreenPreview ? '退出全屏' : '全屏' }}
            </n-button>
          </div>
          <ModelViewer
            model-path="/models/pump.glb"
            :target="[0, 0, 0]"
            :camera-position="[3, 1.74, -4]"
            :model-rotation="[0, 0, 0]"
            :auto-rotate="false"
            :auto-rotate-speed="1"
          />
        </div>
      </n-tab-pane>
      <n-tab-pane name="pid" tab="PID预览">
        <div class="preview-iframe">
          <iframe
            src="http://192.168.6.91:3000/d-solo/ad6rmdl/e696b0-e5bbba-e4bbaa-e8a1a8-e69dbf?orgId=1&from=1779407335672&to=1779428935672&timezone=Asia%2FShanghai&panelId=panel-1"
            width="100%"
            height="100%"
            frameborder="0"
          />
        </div>
      </n-tab-pane>
      <n-tab-pane name="dashboard" tab="仪表板">
        <div class="relative">
          <n-button class="absolute right-4 top-4 z-10" @click="toggleFullscreen">
            {{ isFullscreen ? '退出全屏' : '全屏' }}
          </n-button>
          <iframe
            ref="iframeRef"
            src="http://192.168.6.91:3000/public-dashboards/0e4eb3f75b8c44ada978022f1210b488"
            width="100%"
            height="1000px"
            frameborder="0"
          />
        </div>
      </n-tab-pane>
      <n-tab-pane name="export" tab="数据导出">
        <div class="export-container">
          <div class="export-header">
            <div class="header-left">
              <span class="icon-text">📊</span>
              <span>数据导出工具</span>
            </div>
          </div>

          <n-card class="export-card" :bordered="false">
            <!-- 时间范围 -->
            <div class="step-item">
              <div class="step-header">
                <span class="step-num">1</span>
                <span class="step-title">时间范围</span>
              </div>
              <div class="step-content">
                <n-grid :cols="2" :x-gap="12">
                  <n-gi>
                    <n-date-picker v-model:value="exportForm.startTime" type="datetime" clearable placeholder="开始时间" style="width: 100%" />
                  </n-gi>
                  <n-gi>
                    <n-date-picker v-model:value="exportForm.endTime" type="datetime" clearable placeholder="结束时间" style="width: 100%" />
                  </n-gi>
                </n-grid>
              </div>
            </div>

            <!-- 字段选择 -->
            <div class="step-item">
              <div class="step-header">
                <span class="step-num">2</span>
                <span class="step-title">选择导出字段</span>
              </div>
              <div class="step-content">
                <div v-if="!exportForm.tableName" class="empty-tip">
                  <span>请先在数据源配置页面选择数据表</span>
                </div>
                <div v-else-if="loadingColumns" class="loading-tip">
                  <n-spin size="small" />
                  <span>加载字段中...</span>
                </div>
                <div v-else class="field-list">
                  <div class="field-actions">
                    <n-checkbox :checked="isAllSelected" :indeterminate="isIndeterminate" @update:checked="toggleSelectAll">
                      全选
                    </n-checkbox>
                    <n-button text size="small" @click="reverseSelection">反选</n-button>
                  </div>
                  <n-checkbox-group v-model:value="exportForm.selectedFields">
                    <n-space item-style="display: flex;" vertical>
                      <n-checkbox v-for="col in columnOptions" :key="col.field" :value="col.field" :label="col.comment || col.field" />
                    </n-space>
                  </n-checkbox-group>
                </div>
              </div>
            </div>

            <!-- Action Bar -->
            <div class="action-bar">
              <div class="export-info">
                <span v-if="exportForm.selectedFields.length">已选择 {{ exportForm.selectedFields.length }} 个字段</span>
              </div>
              <n-space>
                <n-button @click="handleReset">重置</n-button>
                <n-button type="primary" :loading="exporting" @click="handleExport">导出 Excel</n-button>
              </n-space>
            </div>
          </n-card>

          <div class="format-info">
            <span>输出格式：Excel 2007+ (.xlsx)</span>
          </div>
        </div>
      </n-tab-pane>
    </n-tabs>
  </AppPage>
</template>

<script setup>
import dayjs from 'dayjs'
import api from '@/api'
import ModelViewer from '@/components/3d/ModelViewer.vue'

defineOptions({ name: '鄄城取水泵站' })

const iframeRef = ref(null)
const preview3DRef = ref(null)
const isFullscreen = ref(false)
const isFullscreenPreview = ref(false)
const exporting = ref(false)
const loadingColumns = ref(false)

const STORAGE_KEY = 'juancheng_export_config'

const defaultForm = {
  datasourceName: null,
  tableName: null,
  selectedFields: [],
  startTime: null,
  endTime: null,
}

const exportForm = ref({ ...defaultForm })

const columnOptions = ref([])

const allFields = computed(() => columnOptions.value.map((col) => col.field))

const isAllSelected = computed(() => columnOptions.value.length > 0 && exportForm.value.selectedFields.length === columnOptions.value.length)

const isIndeterminate = computed(() => exportForm.value.selectedFields.length > 0 && !isAllSelected.value)

onMounted(async () => {
  const handleFullscreenChange = () => {
    isFullscreen.value = !!document.fullscreenElement
    isFullscreenPreview.value = !!document.fullscreenElement
  }
  document.addEventListener('fullscreenchange', handleFullscreenChange)

  // 加载保存的配置
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const savedConfig = JSON.parse(saved)
      exportForm.value.datasourceName = savedConfig.datasourceName
      exportForm.value.tableName = savedConfig.tableName
      if (savedConfig.datasourceName && savedConfig.tableName) {
        await loadColumns(savedConfig.tableName)
      }
    }
  } catch (e) {
    console.error('加载配置失败', e)
  }

  onUnmounted(() => {
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
  })
})

async function loadColumns(tableName) {
  loadingColumns.value = true
  try {
    const res = await api.getDataSourceColumns({
      datasource_name: exportForm.value.datasourceName,
      table_name: tableName,
    })
    columnOptions.value = res.data || []
    exportForm.value.selectedFields = allFields.value
  } catch (e) {
    console.error('获取字段列表失败', e)
    $message.error('获取字段列表失败')
  } finally {
    loadingColumns.value = false
  }
}

function toggleSelectAll(value) {
  exportForm.value.selectedFields = value ? [...allFields.value] : []
}

function reverseSelection() {
  exportForm.value.selectedFields = allFields.value.filter((field) => !exportForm.value.selectedFields.includes(field))
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

function toggleFullscreenPreview() {
  if (!document.fullscreenElement) {
    preview3DRef.value?.requestFullscreen()
    isFullscreenPreview.value = true
  } else {
    document.exitFullscreen()
    isFullscreenPreview.value = false
  }
}

async function handleExport() {
  if (!exportForm.value.datasourceName || !exportForm.value.tableName) {
    $message.warning('请先在数据源配置页面选择数据表')
    return
  }

  exporting.value = true
  try {
    const params = {
      datasource_name: exportForm.value.datasourceName,
      table_name: exportForm.value.tableName,
      columns: exportForm.value.selectedFields.join(','),
    }
    if (exportForm.value.startTime) {
      params.start_time = dayjs(exportForm.value.startTime).format('YYYY-MM-DD HH:mm:ss')
    }
    if (exportForm.value.endTime) {
      params.end_time = dayjs(exportForm.value.endTime).format('YYYY-MM-DD HH:mm:ss')
    }

    const blob = await api.exportData(params)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${exportForm.value.tableName}_${dayjs().format('YYYYMMDDHHmmss')}.xlsx`
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

<style scoped>
.preview-container {
  height: calc(100vh - 280px);
  min-height: 500px;
  padding: 8px;
}

.preview-3d {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background: #1a1a2e;
  height: calc(100vh - 280px);
}

.preview-header {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
}

.fullscreen-btn {
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border: none;
}

.preview-iframe {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  border: 1px solid #f0f0f0;
  height: 800px;
}

.export-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.export-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 0 4px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.icon-text {
  font-size: 20px;
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
</style>