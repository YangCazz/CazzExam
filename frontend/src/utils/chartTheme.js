// ECharts 主题配置工厂：所有颜色读自 CSS 设计令牌，随主题切换联动。
// 纯函数、不绑定组件。用法：const t = chartTheme(); 然后在 option 里引用 t.series.* / t.statusColor(v)。
import { getCssVar } from './theme';

export function chartTheme() {
  const c = (n, fb) => getCssVar(n, fb);
  const series = {
    primary: c('--action-primary', '#5b8cff'),
    violet: c('--action-secondary', '#7a6bb0'),
    success: c('--status-success', '#4db281'),
    warning: c('--status-warning', '#c9a13d'),
    danger: c('--risk-high', '#cf6a68'),
    neutral: c('--status-neutral', '#9aa3b2'),
  };
  return {
    text: c('--text', '#e8ebf2'),
    textMuted: c('--text-muted', '#9aa3b2'),
    textFaint: c('--text-faint', '#626b7c'),
    border: c('--border-strong', 'rgba(148,163,199,.20)'),
    line: c('--text-faint', '#626b7c'),
    label: c('--paper-100', '#d6dae3'),
    surface: c('--surface-solid', '#15181f'),
    tooltip: {
      backgroundColor: c('--ink-900', '#0e1116'),
      borderColor: c('--border-strong', 'rgba(148,163,199,.20)'),
      textStyle: { color: c('--text', '#e8ebf2') },
    },
    series,
    // 掌握度 / 正确率阈值 → 状态色（null 用中性灰 "数据不足"，不上红绿）
    statusColor(a) {
      if (a == null || a === undefined || isNaN(a)) return series.neutral;
      if (a < 0.4) return series.danger;
      if (a < 0.7) return series.warning;
      return series.success;
    },
    nodeColor(m) {
      return (m ?? 0) < 40 ? series.danger : series.primary;
    },
  };
}
