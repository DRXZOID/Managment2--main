<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-backdrop" role="dialog" :aria-labelledby="titleId" @keydown.esc="onCancel">
      <div class="dialog-shell" @click.stop>

        <div class="dialog-header">
          <span :id="titleId" class="dialog-title">
            {{ mode === 'create' ? 'Новий Scrape Job' : 'Редагувати Job' }}
          </span>
          <button class="btn-ghost btn-sm dialog-close" type="button" aria-label="Закрити" @click="onCancel">✕</button>
        </div>

        <div class="dialog-body">
          <form id="sch-job-form" autocomplete="off" @submit.prevent="onSubmit">

            <div class="form-group">
              <label for="sjf-source-key">Source key</label>
              <input id="sjf-source-key" v-model.trim="form.source_key" required
                placeholder="наприклад: hockeyworld" />
            </div>

            <div class="form-group">
              <label for="sjf-runner-type">Runner type</label>
              <select id="sjf-runner-type" v-model="form.runner_type" @change="onRunnerChange">
                <option value="store_category_sync">Синхронізація категорій магазину</option>
                <option value="category_product_sync">Синхронізація товарів категорії</option>
                <option value="all_stores_category_sync">Всі магазини — категорії</option>
              </select>
            </div>

            <!-- Store select -->
            <div v-if="spec.requiresStore" class="form-group">
              <label for="sjf-store">Магазин</label>
              <select id="sjf-store" v-model="form.store_id" @change="onStoreChange">
                <option value="">— оберіть магазин —</option>
                <option v-for="s in stores" :key="s.id" :value="String(s.id)">
                  {{ s.name }}{{ s.is_reference ? ' ★' : '' }}
                </option>
              </select>
              <p v-if="spec.storeHelp" class="field-help">{{ spec.storeHelp }}</p>
            </div>

            <!-- Category select -->
            <div v-if="spec.requiresCategory" class="form-group">
              <label for="sjf-category">Категорія</label>
              <select id="sjf-category" v-model="form.category_id">
                <option value="">— оберіть категорію —</option>
                <option v-for="c in categories" :key="c.id" :value="String(c.id)">
                  {{ c.name }}
                </option>
              </select>
              <p v-if="spec.categoryHelp" class="field-help">{{ spec.categoryHelp }}</p>
            </div>

            <div class="form-group">
              <label class="checkbox-row">
                <input type="checkbox" v-model="form.enabled" />
                <span>Активний (enabled)</span>
              </label>
            </div>
            <div class="form-group">
              <label class="checkbox-row">
                <input type="checkbox" v-model="form.allow_overlap" />
                <span>Дозволити паралельний запуск (allow_overlap)</span>
              </label>
            </div>

            <div class="sch-form-grid">
              <div class="form-group">
                <label for="sjf-priority">Пріоритет</label>
                <input id="sjf-priority" type="number" v-model.number="form.priority"
                  placeholder="0" />
              </div>
              <div class="form-group">
                <label for="sjf-retries">Max retries</label>
                <input id="sjf-retries" type="number" min="0" v-model.number="form.max_retries" />
              </div>
              <div class="form-group">
                <label for="sjf-backoff">Retry backoff (сек)</label>
                <input id="sjf-backoff" type="number" min="1" v-model.number="form.retry_backoff_sec" />
              </div>
              <div class="form-group">
                <label for="sjf-timeout">Timeout (сек)</label>
                <input id="sjf-timeout" type="number" min="1" v-model="form.timeout_sec"
                  placeholder="без обмеження" />
              </div>
            </div>

            <div class="form-group">
              <label for="sjf-concurrency-key">Concurrency key</label>
              <input id="sjf-concurrency-key" v-model="form.concurrency_key"
                placeholder="необов'язково" />
              <p class="field-help">Задачі з однаковим ключем не запускаються паралельно.</p>
            </div>

            <details class="sch-advanced-details">
              <summary>▸ Розширені params (JSON)</summary>
              <div class="form-group" style="margin-top: 8px;">
                <label for="sjf-params">Додаткові params (JSON)</label>
                <textarea id="sjf-params" rows="3" v-model="form.extra_params_json"
                  placeholder='{"extra_key": "value"}' />
                <p class="field-help">Лише додаткові ключі. store_id / category_id заповнюються автоматично.</p>
              </div>
            </details>

            <p v-if="errorMsg" class="field-error" style="margin-top: 10px;">{{ errorMsg }}</p>
          </form>
        </div>

        <div class="dialog-footer">
          <button class="btn-ghost" type="button" @click="onCancel">Скасувати</button>
          <button class="btn" type="submit" form="sch-job-form" :disabled="pending">
            {{ pending ? 'Збереження…' : 'Зберегти' }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getRunnerUiSpec } from '@/types/scheduler'
import type { SchedulerJobDetail } from '@/types/scheduler'
import type { StoreSummary, CategorySummary } from '@/types/store'
import { fetchStores, fetchCategoriesForStore } from '@/api/client'
import { initJobForm } from '../composables/formModels'
import type { JobFormState } from '../composables/formModels'

interface Props {
  open: boolean
  mode: 'create' | 'edit'
  job?: SchedulerJobDetail | null
  pending?: boolean
  errorMsg?: string | null
}
const props = withDefaults(defineProps<Props>(), {
  job: null,
  pending: false,
  errorMsg: null,
})
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', form: JobFormState): void
}>()

const titleId = 'sch-job-dialog-title'

const form = ref<JobFormState>(initJobForm())
const stores = ref<StoreSummary[]>([])
const categories = ref<CategorySummary[]>([])

const spec = computed(() => getRunnerUiSpec(form.value.runner_type))

// Re-init form and load stores when dialog opens
watch(() => props.open, async (isOpen) => {
  if (!isOpen) return
  form.value = initJobForm(props.job ?? null)
  stores.value = await fetchStores().catch(() => [])
  if (form.value.store_id) {
    categories.value = await fetchCategoriesForStore(Number(form.value.store_id)).catch(() => [])
  }
})

function onRunnerChange() {
  form.value.store_id = ''
  form.value.category_id = ''
  categories.value = []
}

async function onStoreChange() {
  form.value.category_id = ''
  categories.value = []
  if (form.value.store_id) {
    categories.value = await fetchCategoriesForStore(Number(form.value.store_id)).catch(() => [])
  }
}

function onSubmit() {
  emit('submit', { ...form.value })
}

function onCancel() {
  emit('close')
}
</script>

<style scoped>
/* reuse dialog shell styles from DialogShell.vue */
.dialog-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.dialog-shell {
  background: #fff; border-radius: 8px; box-shadow: 0 8px 32px rgba(0,0,0,.18);
  min-width: 360px; max-width: 640px; width: 100%; max-height: 90vh;
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

