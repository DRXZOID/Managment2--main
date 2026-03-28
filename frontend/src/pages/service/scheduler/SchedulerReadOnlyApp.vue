<template>
  <div class="scheduler-layout vue-island">
    <!-- ── Left: jobs list ────────────────────────────── -->
    <div class="scheduler-jobs-panel">
      <div class="panel-header" style="padding: 0 0 10px 0;">
        <strong class="panel-title">Задачі</strong>
        <button
          class="btn-ghost btn-sm"
          :disabled="model.loadingJobs.value"
          title="Оновити список"
          @click="model.refresh()"
        >↺ Оновити</button>
      </div>

      <SchedulerJobsList
        :jobs="model.jobs.value"
        :selected-job-id="model.selectedJobId.value"
        :loading="model.loadingJobs.value"
        :error="model.errorJobs.value"
        @select="model.selectJob"
      />
    </div>

    <!-- ── Right: detail panel ──────────────────────── -->
    <div class="scheduler-detail-panel">

      <!-- No selection -->
      <div v-if="!model.selectedJobId.value && !model.loadingJobs.value" class="empty-state">
        <div class="empty-state-icon">⏱</div>
        <p class="empty-state-title">Оберіть задачу</p>
        <p class="empty-state-body">Оберіть задачу зі списку ліворуч, щоб переглянути деталі.</p>
      </div>

      <!-- Loading detail -->
      <div v-else-if="model.loadingDetail.value" class="empty-state">
        <div class="empty-state-icon" aria-live="polite">⏳</div>
        <p class="empty-state-title">Завантаження…</p>
      </div>

      <!-- Error loading detail -->
      <div v-else-if="model.errorDetail.value" class="status-block error" style="margin: 0;">
        ⚠ {{ model.errorDetail.value.message }}
      </div>

      <!-- Job detail -->
      <template v-else-if="model.selectedJob.value">
        <!-- Header (read-only: no mutation buttons) -->
        <div class="panel-header" style="margin-bottom: 16px;">
          <div>
            <span class="sch-job-title">{{ model.selectedJob.value.source_key }}</span>
            <span
              :class="['sch-badge', model.selectedJob.value.enabled ? 'sch-badge-enabled' : 'sch-badge-disabled']"
            >
              {{ model.selectedJob.value.enabled ? 'enabled' : 'disabled' }}
            </span>
          </div>
          <!-- Mutation buttons are intentionally absent in this read-only commit -->
        </div>

        <!-- Job fields -->
        <SchedulerJobDetail :job="model.selectedJob.value" />

        <!-- Schedule card -->
        <SchedulerScheduleCard :schedules="model.selectedSchedules.value" />

        <!-- Recent runs -->
        <SchedulerRunsTable :runs="model.selectedRuns.value" />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SchedulerReadOnlyApp.vue — root component for the Scheduler tab Vue island.
 *
 * This is the first production Vue island on the service page.
 * Mounted by frontend/src/entries/service.ts on #vue-service-scheduler-root.
 *
 * Scope: read-only scheduler UI (jobs list + detail + schedule + runs).
 * Mutation flows (create/edit/run-now/toggle) are deferred to the next commit.
 */
import { onMounted } from 'vue'
import { useSchedulerReadModel } from './composables/useSchedulerReadModel'
import SchedulerJobsList from './components/SchedulerJobsList.vue'
import SchedulerJobDetail from './components/SchedulerJobDetail.vue'
import SchedulerScheduleCard from './components/SchedulerScheduleCard.vue'
import SchedulerRunsTable from './components/SchedulerRunsTable.vue'

const model = useSchedulerReadModel()

// Expose the activate function so service.ts bridge can call it
defineExpose({ activate: model.activate })

// Also trigger activate on mount — this handles the case where the tab is
// already open when the Vue app is first mounted (e.g. direct hash navigation)
onMounted(() => {
  model.activate()
})
</script>

