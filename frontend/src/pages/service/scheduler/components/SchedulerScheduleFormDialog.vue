<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-backdrop" role="dialog" :aria-labelledby="titleId" @keydown.esc="onCancel">
      <div class="dialog-shell" @click.stop>

        <div class="dialog-header">
          <span :id="titleId" class="dialog-title">
            {{ schedule ? 'Редагувати розклад' : 'Новий розклад' }}
          </span>
          <button class="btn-ghost btn-sm dialog-close" type="button" aria-label="Закрити" @click="onCancel">✕</button>
        </div>

        <div class="dialog-body">
          <form id="sch-schedule-form" autocomplete="off" @submit.prevent="onSubmit">

            <div class="form-group">
              <label for="ssf-type">Тип розкладу</label>
              <select id="ssf-type" v-model="form.schedule_type">
                <option value="interval">⏱ Інтервал (кожні N секунд)</option>
                <option value="cron">🗓 Cron (за розкладом)</option>
              </select>
              <p class="field-help">
                {{ form.schedule_type === 'interval'
                  ? 'Запускати через рівні проміжки часу.'
                  : 'Запускати за cron-розкладом (у вибраному timezone).' }}
              </p>
            </div>

            <!-- Interval -->
            <div v-if="form.schedule_type === 'interval'" class="form-group">
              <label for="ssf-interval">Інтервал (секунд)</label>
              <input id="ssf-interval" type="number" min="60" v-model="form.interval_sec"
                placeholder="3600 = 1 година" />
              <p class="field-help">Мінімум 60 секунд. 3600 = 1 год, 86400 = 1 день.</p>
            </div>

            <!-- Cron -->
            <template v-else>
              <div class="form-group">
                <label for="ssf-cron">Cron вираз</label>
                <input id="ssf-cron" v-model.trim="form.cron_expr"
                  placeholder="0 9 * * 1-5" />
                <p class="field-help">
                  5 полів: хв год д-місяця місяць д-тижня.
                  Наприклад: <code>0 9 * * 1-5</code> = щоденно о 09:00 пн–пт.
                </p>
              </div>
              <div class="form-group">
                <label for="ssf-timezone">Timezone (IANA)</label>
                <input id="ssf-timezone" v-model.trim="form.timezone"
                  placeholder="UTC, Europe/Kyiv, America/New_York…" />
              </div>
            </template>

            <div class="sch-form-grid">
              <div class="form-group">
                <label for="ssf-jitter">Jitter (сек)</label>
                <input id="ssf-jitter" type="number" min="0" v-model.number="form.jitter_sec"
                  placeholder="0 = вимк" />
              </div>
              <div class="form-group">
                <label for="ssf-misfire">Misfire policy</label>
                <select id="ssf-misfire" v-model="form.misfire_policy">
                  <option value="skip">skip — пропустити прострочені</option>
                  <option value="run_once">run_once — виконати один раз</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="checkbox-row">
                <input type="checkbox" v-model="form.enabled" />
                <span>Розклад активний</span>
              </label>
            </div>

            <p v-if="errorMsg" class="field-error" style="margin-top: 10px;">{{ errorMsg }}</p>
          </form>
        </div>

        <div class="dialog-footer">
          <button class="btn-ghost" type="button" @click="onCancel">Скасувати</button>
          <button class="btn" type="submit" form="sch-schedule-form" :disabled="pending">
            {{ pending ? 'Збереження…' : 'Зберегти' }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { initScheduleForm } from '../composables/formModels'
import type { ScheduleFormState } from '../composables/formModels'
import type { SchedulerSchedule } from '@/types/scheduler'

interface Props {
  open: boolean
  schedule?: SchedulerSchedule | null
  pending?: boolean
  errorMsg?: string | null
}
const props = withDefaults(defineProps<Props>(), {
  schedule: null,
  pending: false,
  errorMsg: null,
})
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', form: ScheduleFormState): void
}>()

const titleId = 'sch-schedule-dialog-title'
const form = ref<ScheduleFormState>(initScheduleForm())

// Re-init form when dialog opens
watch(() => props.open, (isOpen) => {
  if (!isOpen) return
  form.value = initScheduleForm(props.schedule ?? null)
})

function onSubmit() {
  emit('submit', { ...form.value })
}

function onCancel() {
  emit('close')
}
</script>

<style scoped>
.dialog-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.dialog-shell {
  background: #fff; border-radius: 8px; box-shadow: 0 8px 32px rgba(0,0,0,.18);
  min-width: 360px; max-width: 560px; width: 100%; max-height: 90vh;
  display: flex; flex-direction: column; overflow: hidden;
}
.dialog-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px 12px; border-bottom: 1px solid #e5e7eb;
}
.dialog-title { font-weight: 700; font-size: 1rem; }
.dialog-close { background: none; border: none; cursor: pointer; font-size: 1.1rem; color: #6b7280; }
.dialog-body { padding: 20px; overflow-y: auto; flex: 1; }
.dialog-footer {
  padding: 12px 20px; border-top: 1px solid #e5e7eb;
  display: flex; gap: 8px; justify-content: flex-end;
}
</style>

