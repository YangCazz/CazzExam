// 读取设计令牌的 JS 入口：让业务组件 / ECharts 从 CSS 变量取值，而非硬编码 hex。
// 未来接入浅色模式时，只需切换 :root 或 [data-theme] 上的变量，此处无需改动。
export function getCssVar(name, fallback = '') {
  if (typeof document === 'undefined') return fallback;
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name);
  const v = (raw || '').trim();
  return v || fallback;
}

// 快捷按状态语义取色（返回 RGB 字符串）
export function cssVar(name, fallback = '') {
  return getCssVar(name, fallback);
}
