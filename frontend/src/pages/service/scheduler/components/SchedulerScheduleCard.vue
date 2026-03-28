<template>
  <div class="subpanel" style="margin-top: 16px;">
    <div class="panel-header">
      <strong class="panel-title">Розклад</strong>
    </div>

    <!-- No schedule -->
    <div v-if="!schedule" class="sch-no-schedule">Розклад не налаштовано.</div>

    <!-- Schedule grid -->
    <div v-else class="sch-info-grid" style="margin-top: 8px;">
      <div class="sch-info-row">
        <span class="sch-info-label">Тип</span>
        <span class="sch-info-value">{{ schedule.schedule_type }}</span>
      </div>
      <div class="sch-info-row">
        <span class="sch-info-label">Активний</span>
        <span class="sch-info-value">
          <span :class="['sch-badge', schedule.enabled ? 'sch-badge-enabled' : 'sch-badge-disabled']">
            {{ schedule.enabled ? 'enabled' : 'disabled' }}
          </span>
        </span>
      </div>
      <div v-if="schedule.interval_sec != null" class="sch-info-row">
        <span class="sch-info-label">Інтервал</span>
        <span class="sch-info-value">{{ fmtInterval(schedule.interval_sec) }}</span>
      </div>
      <div v-if="schedule.cron_expr" class="sch-info-row">
        <span class="sch-info-label">Cron</span>
        <span class="sch-info-value">
          <code class="sch-cron-code">{{ schedule.cron_expr }}</code>
        </span>
      </div>
      <div class="sch-info-row">
        <span class="sch-info-label">Timezone</span>
        <span class="sch-info-value">{{ schedule.timezone || 'UTC' }}</span>
      </div>
      <div class="sch-info-row">
        <span class="sch-info-label">Jitter</span>
        <span class="sch-info-value">{{ schedule.jitter_sec }}s</span>
      </div>
      <div class="sch-info-row">
        <span class="sch-info-label">Misfire policy</span>
        <span class="sch-info-value">{{ schedule.misfire_policy }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SchedulerScheduleCard.vue — schedule summary sub-panel.
 * Read-only. Uses existing .subpanel + .sch-info-grid CSS.
 */
import { computed } from 'vue'
import type { SchedulerSchedule } from '@/types/scheduler'

interface Props {
  schedules: SchedulerSchedule[]
}

const props = defineProps<Props>()

// Primary schedule is the first enabled one, or the first one if none enabled
const schedule = computed<SchedulerSchedule | null>(() => {
  if (!props.schedules.length) return null
  return props.schedules.find((s) => s.enabled) ?? props.schedules[0]
})

function fmtInterval(sec: number): string {
  if (sec < 60) return `${sec}с`
  if (sec < 3600) return `${Math.round(sec / 60)}хв`
  if (sec < 86400) return `${(sec / 3600).toFixed(1)}год`
  return `${(sec / 86400).toFixed(1)}дн`
}
</script>

