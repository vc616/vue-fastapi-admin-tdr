<template>
  <AppPage>
    <n-card class="config-card" :bordered="false">
      <div class="config-header">
        <span class="icon">⚙️</span>
        <span>数据源配置</span>
      </div>

      <n-grid :cols="2" :x-gap="24" responsive="screen" :item-responsive="true">
        <n-gi :span="2" :md="1">
          <div class="step-item">
            <div class="step-header">
              <span class="step-num">1</span>
              <span class="step-title">选择数据源</span>
            </div>
            <div class="step-content">
              <n-select
                v-model:value="config.datasourceName"
                :options="datasourceOptions"
                placeholder="请选择数据源"
                filterable
                clearable
                @update:value="handleDatasourceChange"
              />
            </div>
          </div>
        </n-gi>

        <n-gi :span="2" :md="1">
          <div class="step-item">
            <div class="step-header">
              <span class="step-num">2</span>
              <span class="step-title">选择数据表</span>
            </div>
            <div class="step-content">
              <n-select
                v-model:value="config.tableName"
                :options="tableOptions"
                placeholder="请先选择数据源"
                filterable
                clearable
                :loading="loadingTables"
                :disabled="!config.datasourceName"
                @update:value="handleTableChange"
              />
            </div>
          </div>
        </n-gi>
      </n-grid>

      <div class="save-bar">
        <n-space>
          <n-button @click="handleReset">重置</n-button>
          <n-button type="primary" @click="handleSave">保存配置</n-button>
        </n-space>
        <n-tag v-if="savedText" type="success" size="small">{{ savedText }}</n-tag>
      </div>
    </n-card>
  </AppPage>
</template>

<script setup>
import api from '@/api'

defineOptions({ name: '数据源配置' })

const loadingTables = ref(false)
const STORAGE_KEY = 'juancheng_export_config'

const config = ref({
  datasourceName: null,
  tableName: null,
})

const datasourceOptions = ref([])
const tableOptions = ref([])
const savedText = ref('')

onMounted(async () => {
  // 加载保存的配置
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const savedConfig = JSON.parse(saved)
      config.value.datasourceName = savedConfig.datasourceName
      config.value.tableName = savedConfig.tableName
      if (savedConfig.datasourceName) {
        await loadTables(savedConfig.datasourceName)
      }
    }
  } catch (e) {
    console.error('加载配置失败', e)
  }
})

async function loadDatasources() {
  try {
    const res = await api.getDataSourceList({ page: 1, page_size: 100 })
    datasourceOptions.value = (res.data || []).map((item) => ({
      label: item.name,
      value: item.name,
    }))
  } catch (e) {
    console.error('获取数据源列表失败', e)
  }
}

async function handleDatasourceChange(value) {
  config.value.tableName = null
  tableOptions.value = []
  if (!value) {
    return
  }
  await loadTables(value)
}

async function loadTables(datasourceName) {
  loadingTables.value = true
  try {
    const res = await api.getDataSourceTables({ datasource_name: datasourceName })
    tableOptions.value = (res.data || []).map((name) => ({
      label: name,
      value: name,
    }))
  } catch (e) {
    console.error('获取表列表失败', e)
    $message.error('获取表列表失败')
  } finally {
    loadingTables.value = false
  }
}

function handleTableChange(value) {
  if (!value) {
    config.value.tableName = null
  }
}

function handleReset() {
  config.value.datasourceName = null
  config.value.tableName = null
  tableOptions.value = []
  localStorage.removeItem(STORAGE_KEY)
  savedText.value = ''
}

function handleSave() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config.value))
    savedText.value = '配置已保存'
    setTimeout(() => {
      savedText.value = ''
    }, 2000)
  } catch (e) {
    console.error('保存配置失败', e)
    $message.error('保存配置失败')
  }
}

// 初始化加载数据源
loadDatasources()
</script>

<style scoped>
.config-card {
  max-width: 800px;
  margin: 40px auto;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.config-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.icon {
  font-size: 20px;
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

.save-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>