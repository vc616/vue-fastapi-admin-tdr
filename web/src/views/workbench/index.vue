<template>
  <AppPage :show-footer="false">
    <div flex-1>
      <!-- 欢迎卡片 -->
      <n-card rounded-10 mb-15>
        <div flex items-center justify-between>
          <div flex items-center>
            <img rounded-full width="60" :src="userStore.avatar || 'https://cdn.mairui.com/hsui/head.jpg'" />
            <div ml-10>
              <p text-20 font-semibold>{{ $t('views.workbench.text_hello', { username: userStore.name || 'Admin' }) }}</p>
              <p mt-5 text-14 op-60>{{ today }} &nbsp; {{ $t('views.workbench.text_welcome') }}</p>
            </div>
          </div>
        </div>
      </n-card>

      <!-- 统计卡片 -->
      <n-grid :x-gap="15" :y-gap="15" :cols="6" responsive="screen" item-responsive>
        <n-grid-item>
          <n-card rounded-10>
            <n-statistic :label="$t('views.workbench.label_total_users')" :value="stats.total_users" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card rounded-10>
            <n-statistic :label="$t('views.workbench.label_active_users')" :value="stats.active_users" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card rounded-10>
            <n-statistic :label="$t('views.workbench.label_total_roles')" :value="stats.total_roles" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card rounded-10>
            <n-statistic :label="$t('views.workbench.label_total_menus')" :value="stats.total_menus" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card rounded-10>
            <n-statistic :label="$t('views.workbench.label_total_apis')" :value="stats.total_apis" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card rounded-10>
            <n-statistic :label="$t('views.workbench.label_today_audits')" :value="stats.today_audit_count" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 近7日操作趋势 -->
      <n-card :title="$t('views.workbench.label_weekly_trend')" size="small" mt-15 rounded-10>
        <div ref="chartRef" h-300 />
      </n-card>

      <!-- 最近操作日志 -->
      <n-card :title="$t('views.workbench.label_recent_audit')" size="small" mt-15 rounded-10>
        <n-data-table
          :columns="auditColumns"
          :data="stats.recent_audits"
          :pagination="false"
          size="small"
          :bordered="false"
        />
      </n-card>

      <!-- 快捷操作 -->
      <n-card :title="$t('views.workbench.label_quick_action')" size="small" mt-15 rounded-10>
        <n-space>
          <n-button @click="router.push('/system/user')">
            <TheIcon icon="material-symbols:person" :size="18" class="mr-5" />
            {{ $t('views.workbench.label_user_mgmt') }}
          </n-button>
          <n-button @click="router.push('/system/role')">
            <TheIcon icon="material-symbols:shield" :size="18" class="mr-5" />
            {{ $t('views.workbench.label_role_mgmt') }}
          </n-button>
          <n-button @click="router.push('/system/menu')">
            <TheIcon icon="material-symbols:menu" :size="18" class="mr-5" />
            {{ $t('views.workbench.label_menu_mgmt') }}
          </n-button>
          <n-button @click="router.push('/system/auditlog')">
            <TheIcon icon="material-symbols:receipt-long" :size="18" class="mr-5" />
            {{ $t('views.workbench.label_audit_log') }}
          </n-button>
        </n-space>
      </n-card>
    </div>
  </AppPage>
</template>

<script setup>
import { h, onMounted, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { NTag } from 'naive-ui'
import * as echarts from 'echarts'
import { useUserStore } from '@/store'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

const router = useRouter()
const userStore = useUserStore()
const chartRef = ref(null)
let chart = null

const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

const stats = ref({
  total_users: 0,
  active_users: 0,
  total_roles: 0,
  total_menus: 0,
  total_apis: 0,
  total_depts: 0,
  today_audit_count: 0,
  recent_audits: [],
})

const auditColumns = [
  { title: 'views.workbench.label_column_time', key: 'created_at', width: 160 },
  { title: 'views.workbench.label_column_user', key: 'username', width: 100 },
  { title: 'views.workbench.label_column_module', key: 'module', width: 100 },
  { title: 'views.workbench.label_column_summary', key: 'summary', ellipsis: { tooltip: true } },
  {
    title: 'views.workbench.label_column_method',
    key: 'method',
    width: 80,
    align: 'center',
    render(row) {
      const colorMap = { GET: 'success', POST: 'info', PUT: 'warning', DELETE: 'error', PATCH: 'warning' }
      const type = colorMap[row.method] || 'default'
      return h(NTag, { type, bordered: false, style: 'font-size: 12px' }, { default: () => row.method })
    },
  },
  {
    title: 'views.workbench.label_column_status',
    key: 'status',
    width: 80,
    align: 'center',
    render(row) {
      const ok = row.status === 200
      return h(NTag, { type: ok ? 'success' : 'error', bordered: false }, { default: () => row.status })
    },
  },
  {
    title: 'views.workbench.label_column_duration',
    key: 'response_time',
    width: 100,
    align: 'center',
    render(row) {
      return h('span', {}, `${row.response_time}ms`)
    },
  },
]

async function loadDashboard() {
  try {
    const res = await api.getStatisticsDashboard()
    stats.value = res.data
    await nextTick()
    renderChart()
  } catch (e) {
    console.error('loadDashboard error', e)
  }
}

async function renderChart() {
  if (!chartRef.value) return
  try {
    const res = await api.getStatisticsChart({ type: 'weekly' })
    const dailyCounts = res.data.daily_counts
    const dates = dailyCounts.map((d) => d.date)
    const values = dailyCounts.map((d) => d.count)

    chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates, boundaryGap: false },
      yAxis: { type: 'value', minInterval: 1 },
      series: [
        {
          name: '操作次数',
          type: 'line',
          smooth: true,
          data: values,
          areaStyle: { opacity: 0.2 },
          lineStyle: { width: 2 },
          itemStyle: { color: '#63b8ff' },
        },
      ],
    })
  } catch (e) {
    console.error('renderChart error', e)
  }
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('resize', () => chart?.resize())
})
</script>