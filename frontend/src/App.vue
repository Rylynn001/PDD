<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const API_BASE = 'http://localhost:8000/api/v1'

interface TradeRow {
  [key: string]: string | number
}

const anti = ref('')
const cookie = ref('')
const dateRange = ref<[string, string] | null>(null)

const loading = ref(false)
const exporting = ref(false)
const capturing = ref(false)
const tableData = ref<TradeRow[]>([])
const lastPayload = ref<object | null>(null)

const columns = computed(() => (tableData.value.length ? Object.keys(tableData.value[0]) : []))
const hasData = computed(() => tableData.value.length > 0)

async function handleCapture() {
  capturing.value = true
  try {
    const resp = await fetch(`${API_BASE}/auth/capture`)
    const json = await resp.json()
    if (!resp.ok) {
      ElMessage.error(`捕获失败：${json.detail ?? resp.status}`)
      return
    }
    anti.value = json.anti ?? ''
    cookie.value = json.cookie ?? ''
    ElMessage.success('认证信息已自动填充')
  } catch (e: unknown) {
    ElMessage.error(`网络错误：${(e as Error).message}`)
  } finally {
    capturing.value = false
  }
}

function validate() {
  if (!anti.value.trim()) return '请填写 Anti-Content'
  if (!cookie.value.trim()) return '请填写 Cookie'
  if (!dateRange.value?.[0] || !dateRange.value?.[1]) return '请选择日期范围'
  if (dateRange.value[0] > dateRange.value[1]) return '开始日期不能晚于结束日期'
  return null
}

async function handleQuery() {
  const err = validate()
  if (err) { ElMessage.error(err); return }

  const payload = {
    anti: anti.value.trim(),
    cookie: cookie.value.trim(),
    start_date: dateRange.value![0],
    end_date: dateRange.value![1],
  }

  loading.value = true
  tableData.value = []

  try {
    const resp = await fetch(`${API_BASE}/trade/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const json = await resp.json()
    if (!resp.ok) {
      ElMessage.error(`请求失败：${json.detail ?? resp.status}`)
      return
    }
    lastPayload.value = payload
    tableData.value = json.data
    ElMessage.success(`查询成功，共 ${json.total} 条数据`)
  } catch (e: unknown) {
    ElMessage.error(`网络错误：${(e as Error).message}`)
  } finally {
    loading.value = false
  }
}

async function handleExport() {
  if (!lastPayload.value) return
  exporting.value = true

  try {
    const resp = await fetch(`${API_BASE}/trade/query/excel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(lastPayload.value),
    })
    if (!resp.ok) {
      const json = await resp.json()
      ElMessage.error(`导出失败：${json.detail ?? resp.status}`)
      return
    }
    const blob = await resp.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    const p = lastPayload.value as { start_date: string; end_date: string }
    a.href = url
    a.download = `pdd_trade_${p.start_date}_${p.end_date}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e: unknown) {
    ElMessage.error(`网络错误：${(e as Error).message}`)
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <div class="page">
    <!-- 背景光晕 -->
    <div class="bg">
      <div class="blob blob-1" />
      <div class="blob blob-2" />
      <div class="blob blob-3" />
    </div>

    <!-- 顶栏 -->
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <svg class="logo-mark" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
          <span>PDD 数据</span>
        </div>
        <div class="header-badge">交易分析</div>
      </div>
    </header>

    <main class="main">
      <!-- 标题区 -->
      <div class="hero">
        <h1 class="hero-title">交易数据查询</h1>
        <p class="hero-sub">填写认证信息与日期范围，拉取店铺核心交易指标</p>
      </div>

      <!-- 表单卡片 -->
      <div class="glass-card form-card">
        <div class="form-grid">
          <!-- Anti-Content -->
          <div class="field field-full">
            <label class="label">Anti-Content</label>
            <div class="input-wrap">
              <textarea
                v-model="anti"
                class="glass-textarea"
                rows="3"
                placeholder="粘贴 anti-content 值…"
              />
            </div>
          </div>

          <!-- Cookie -->
          <div class="field field-full">
            <label class="label">Cookie</label>
            <div class="input-wrap">
              <textarea
                v-model="cookie"
                class="glass-textarea"
                rows="3"
                placeholder="粘贴 Cookie 值…"
              />
            </div>
          </div>

          <!-- 日期范围 -->
          <div class="field field-full">
            <label class="label">日期范围</label>
            <div class="input-wrap date-wrap">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                value-format="YYYY-MM-DD"
                range-separator="→"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                :teleported="true"
                popper-class="glass-date-popper"
              />
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="card-actions">
          <button
            class="btn btn-capture"
            :disabled="capturing || loading || exporting"
            @click="handleCapture"
          >
            <span v-if="capturing" class="spinner spinner-ghost" />
            <svg v-else viewBox="0 0 16 16" fill="none" width="14" height="14">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 5v3l2 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ capturing ? '捕获中…' : '自动捕获认证' }}
          </button>
          <button
            class="btn btn-primary"
            :disabled="loading || exporting"
            @click="handleQuery"
          >
            <span v-if="loading" class="spinner" />
            <svg v-else viewBox="0 0 16 16" fill="none" width="14" height="14">
              <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.5"/>
              <path d="M11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ loading ? '查询中…' : '查询数据' }}
          </button>
          <button
            class="btn btn-ghost"
            :disabled="!hasData || loading || exporting"
            @click="handleExport"
          >
            <span v-if="exporting" class="spinner spinner-ghost" />
            <svg v-else viewBox="0 0 16 16" fill="none" width="14" height="14">
              <path d="M8 2v8M5 7l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            {{ exporting ? '导出中…' : '导出 Excel' }}
          </button>
        </div>
      </div>

      <!-- 数据表格 -->
      <Transition name="rise">
        <div v-if="hasData" class="glass-card table-card">
          <div class="table-meta">
            <span class="table-label">查询结果</span>
            <span class="table-count">{{ tableData.length }} 条</span>
          </div>
          <div class="table-scroll">
            <table class="data-table">
              <thead>
                <tr>
                  <th v-for="col in columns" :key="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, i) in tableData"
                  :key="i"
                  class="data-row"
                  :style="{ animationDelay: `${i * 25}ms` }"
                >
                  <td v-for="col in columns" :key="col">{{ row[col] ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Transition>
    </main>
  </div>
</template>

<style scoped>
/* ── 页面容器 ── */
.page {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* ── 背景光晕 ── */
.bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.55;
  animation: breathe 8s ease-in-out infinite;
}

.blob-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #1a3a6e 0%, transparent 70%);
  top: -200px;
  left: -150px;
  animation-delay: 0s;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #0e2847 0%, transparent 70%);
  top: 30%;
  right: -100px;
  animation-delay: 3s;
}

.blob-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #1c1c30 0%, transparent 70%);
  bottom: 5%;
  left: 20%;
  animation-delay: 5s;
}

@keyframes breathe {
  0%, 100% { transform: scale(1) translate(0, 0); opacity: 0.55; }
  33%       { transform: scale(1.08) translate(20px, -15px); opacity: 0.7; }
  66%       { transform: scale(0.94) translate(-10px, 20px); opacity: 0.45; }
}

/* ── 顶栏 ── */
.header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(15, 15, 19, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.header-inner {
  max-width: 780px;
  margin: 0 auto;
  padding: 0 24px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 15px;
  font-weight: 600;
  color: #e8e8ed;
  letter-spacing: -0.01em;
}

.logo-mark {
  width: 20px;
  height: 20px;
  color: #6d9eff;
}

.header-badge {
  font-size: 11px;
  font-weight: 500;
  color: rgba(109, 158, 255, 0.8);
  background: rgba(109, 158, 255, 0.1);
  border: 1px solid rgba(109, 158, 255, 0.2);
  border-radius: 20px;
  padding: 3px 10px;
  letter-spacing: 0.02em;
}

/* ── 主内容 ── */
.main {
  position: relative;
  z-index: 1;
  max-width: 780px;
  margin: 0 auto;
  padding: 52px 24px 80px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── 标题 ── */
.hero {
  margin-bottom: 8px;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #f0f0f5;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.hero-sub {
  margin-top: 6px;
  font-size: 14px;
  color: rgba(235, 235, 245, 0.45);
  letter-spacing: -0.01em;
}

/* ── 毛玻璃卡片 ── */
.glass-card {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 18px;
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.3),
    0 12px 40px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.07);
  transition: box-shadow 0.4s ease, border-color 0.4s ease;
}

.glass-card:hover {
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.3),
    0 16px 48px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(109, 158, 255, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.12);
}

/* ── 表单 ── */
.form-card {
  padding: 28px;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(235, 235, 245, 0.5);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.input-wrap {
  position: relative;
}

.glass-textarea {
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 12px 14px;
  font-family: inherit;
  font-size: 13.5px;
  color: #e8e8ed;
  outline: none;
  resize: none;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
  line-height: 1.6;
}

.glass-textarea::placeholder {
  color: rgba(235, 235, 245, 0.25);
}

.glass-textarea:focus {
  border-color: rgba(109, 158, 255, 0.45);
  box-shadow: 0 0 0 3px rgba(109, 158, 255, 0.1), 0 0 20px rgba(109, 158, 255, 0.06);
  background: rgba(109, 158, 255, 0.03);
}

/* 日期选择器 */
.date-wrap :deep(.el-date-editor) {
  width: 100% !important;
  background: rgba(255, 255, 255, 0.04) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  height: 42px !important;
  padding: 0 14px !important;
  transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}

.date-wrap :deep(.el-date-editor:hover),
.date-wrap :deep(.el-date-editor.is-active) {
  border-color: rgba(109, 158, 255, 0.45) !important;
  box-shadow: 0 0 0 3px rgba(109, 158, 255, 0.1), 0 0 20px rgba(109, 158, 255, 0.06) !important;
  background: rgba(109, 158, 255, 0.03) !important;
}

.date-wrap :deep(.el-range-input) {
  background: transparent !important;
  color: #f0f0f5 !important;
  font-family: inherit !important;
  font-size: 14px !important;
  font-weight: 500 !important;
}

.date-wrap :deep(.el-range-input::placeholder) {
  color: rgba(235, 235, 245, 0.45) !important;
  font-weight: 400 !important;
}

.date-wrap :deep(.el-range-separator) {
  color: rgba(235, 235, 245, 0.75) !important;
  font-size: 15px !important;
  font-weight: 600 !important;
}

.date-wrap :deep(.el-input__prefix),
.date-wrap :deep(.el-input__suffix) {
  color: rgba(235, 235, 245, 0.6) !important;
}

/* ── 操作按钮 ── */
.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 28px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px 22px;
  border-radius: 10px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  outline: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  user-select: none;
  letter-spacing: -0.01em;
}

.btn:active:not(:disabled) {
  transform: scale(0.97);
}

.btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #3b6cdb 0%, #2855c4 100%);
  color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3), 0 4px 16px rgba(59, 108, 219, 0.35);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #4a7aeb 0%, #3463d4 100%);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3), 0 8px 24px rgba(59, 108, 219, 0.45);
  transform: translateY(-1px);
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(235, 235, 245, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-ghost:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.18);
  color: #e8e8ed;
  transform: translateY(-1px);
}

.btn-capture {
  background: rgba(52, 199, 89, 0.12);
  color: rgba(52, 199, 89, 0.9);
  border: 1px solid rgba(52, 199, 89, 0.2);
}

.btn-capture:hover:not(:disabled) {
  background: rgba(52, 199, 89, 0.2);
  border-color: rgba(52, 199, 89, 0.35);
  color: #34c759;
  transform: translateY(-1px);
}

/* ── 加载旋转 ── */
.spinner {
  width: 13px;
  height: 13px;
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.65s linear infinite;
  flex-shrink: 0;
}

.spinner-ghost {
  border-color: rgba(235, 235, 245, 0.2);
  border-top-color: rgba(235, 235, 245, 0.7);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── 数据表格 ── */
.table-card {
  overflow: hidden;
}

.table-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 22px 0;
}

.table-label {
  font-size: 13px;
  font-weight: 600;
  color: rgba(235, 235, 245, 0.7);
  letter-spacing: -0.01em;
}

.table-count {
  font-size: 12px;
  font-weight: 500;
  color: rgba(109, 158, 255, 0.8);
  background: rgba(109, 158, 255, 0.1);
  border: 1px solid rgba(109, 158, 255, 0.15);
  border-radius: 20px;
  padding: 2px 10px;
}

.table-scroll {
  overflow-x: auto;
  padding: 14px 0 0;
  /* 滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

.table-scroll::-webkit-scrollbar {
  height: 4px;
}

.table-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.table-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  padding: 10px 18px;
  text-align: left;
  font-weight: 500;
  color: rgba(235, 235, 245, 0.4);
  white-space: nowrap;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
  letter-spacing: 0.01em;
  font-size: 12px;
}

.data-table td {
  padding: 11px 18px;
  color: rgba(235, 235, 245, 0.85);
  white-space: nowrap;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.data-row {
  animation: row-in 0.3s cubic-bezier(0.16, 1, 0.3, 1) both;
  transition: background 0.15s ease;
}

.data-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.data-row:last-child td {
  border-bottom: none;
}

@keyframes row-in {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── 页面过渡 ── */
.rise-enter-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.rise-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
</style>
