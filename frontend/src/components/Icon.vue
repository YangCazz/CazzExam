<script setup>
defineProps({ name: { type: String, required: true }, size: { type: Number, default: 16 } });
const S = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"';
const icons = {
  home: '<svg ' + S + '><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>',
  book: '<svg ' + S + '><path d="M4 5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2z"/><path d="M4 19a2 2 0 0 1 2-2h14"/></svg>',
  target: '<svg ' + S + '><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/></svg>',
  network: '<svg ' + S + '><circle cx="5" cy="6" r="2.2"/><circle cx="19" cy="6" r="2.2"/><circle cx="12" cy="18" r="2.2"/><path d="M6.8 7.4 10.8 16M17.2 7.4 13.2 16M7 6h10"/></svg>',
  database: '<svg ' + S + '><ellipse cx="12" cy="5.5" rx="8" ry="2.8"/><path d="M4 5.5V12c0 1.6 3.6 2.8 8 2.8s8-1.2 8-2.8V5.5"/><path d="M4 12v6.5c0 1.6 3.6 2.8 8 2.8s8-1.2 8-2.8V12"/></svg>',
  exam: '<svg ' + S + '><rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M8.5 8h7M8.5 12h7M8.5 16h4"/></svg>',
  wrong: '<svg ' + S + '><path d="M12 3 2.5 20h19z"/><path d="M12 9.5v4.5"/><circle cx="12" cy="17.5" r=".8"/></svg>',
  calendar: '<svg ' + S + '><rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 9.5h16M8 3v4M16 3v4"/><path d="M8.5 14h7"/></svg>',
  chart: '<svg ' + S + '><path d="M4 20V10M10 20V4M16 20v-8"/><path d="M22 20H2"/></svg>',
  essay: '<svg ' + S + '><path d="M6 2.5h9l5 5v14H6z"/><path d="M15 2.5v5h5M9 12h6M9 16h6"/></svg>',
  gear: '<svg ' + S + '><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/></svg>',
};
</script>
<template>
  <span class="ico" :style="{ width: size + 'px', height: size + 'px' }" v-html="icons[name] || ''" />
</template>
