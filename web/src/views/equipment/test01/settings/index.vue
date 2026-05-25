<template>
  <AppPage>
    <n-card :bordered="false">
      <h3 class="mb-4">测试设备01 - 设置</h3>
      <n-form label-placement="left" label-width="120">
        <n-form-item label="设备名称">
          <n-input value="测试设备01" />
        </n-form-item>
        <n-form-item label="设备状态">
          <n-switch :checked="true" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input type="textarea" placeholder="请输入备注信息" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary">保存</n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </AppPage>
</template>

<script setup>
defineOptions({ name: '测试设备01设置' })
</script>
