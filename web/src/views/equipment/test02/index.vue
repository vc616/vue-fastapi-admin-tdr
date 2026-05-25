<template>
  <AppPage>
    <n-tabs type="line" animated>
      <n-tab-pane name="preview" tab="设备预览">
        <div class="p-4">
          <h3>测试设备02 - 设备预览</h3>
          <p>设备预览内容占位...</p>
        </div>
      </n-tab-pane>
      <n-tab-pane name="dashboard" tab="仪表板">
        <div class="p-4">
          <h3>测试设备02 - 仪表板</h3>
          <p>仪表板内容占位...</p>
        </div>
      </n-tab-pane>
      <n-tab-pane name="info" tab="设备信息">
        <div class="p-4">
          <h3>测试设备02 - 设备信息</h3>
          <p>设备信息内容占位...</p>
        </div>
      </n-tab-pane>
    </n-tabs>
  </AppPage>
</template>

<script setup>
defineOptions({ name: '测试设备02' })
</script>
