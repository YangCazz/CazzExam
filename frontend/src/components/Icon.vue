<script setup>
// 图标统一走 lucide-vue-next（MIT），在此与业务 name 做映射。
// 只导入用到的图标以保 tree-shaking；图标默认 stroke=currentColor 随文字色。
import { computed } from 'vue';
import {
  Home, BookOpen, Target, Network, Database, FileText, TriangleAlert,
  Calendar, BarChart3, Settings, Briefcase, ClipboardCheck, PenLine,
  ArrowRight, ChevronRight, CheckCircle2, Clock, TrendingUp, PieChart,
  GitBranch, FlaskConical, Sigma, Library, Laptop, RefreshCcw,
} from 'lucide-vue-next';

const props = defineProps({ name: { type: String, required: true }, size: { type: Number, default: 16 } });
const icons = {
  home: Home, book: BookOpen, target: Target, network: Network, database: Database,
  essay: FileText, wrong: TriangleAlert, calendar: Calendar, chart: BarChart3,
  gear: Settings, case: Briefcase, exam: ClipboardCheck, practice: PenLine,
  'arrow-right': ArrowRight, 'chevron-right': ChevronRight, 'check-circle': CheckCircle2,
  clock: Clock, 'trending-up': TrendingUp, pie: PieChart, branch: GitBranch,
  lab: FlaskConical, sigma: Sigma, library: Library, laptop: Laptop,
  restart: RefreshCcw,
};
const icon = computed(() => icons[props.name] || null);
</script>
<template>
  <span class="ico" :style="{ width: size + 'px', height: size + 'px' }">
    <component :is="icon" v-if="icon" :size="size" :stroke-width="1.75" aria-hidden="true" />
  </span>
</template>
