<template>
  <div class="comparison-page">

    <!-- ── Store selects + page status ──────────────────────────── -->
    <ComparisonFilters
      :reference-stores="page.referenceStores.value"
      :target-stores="page.targetStores.value"
      :reference-store-id="page.referenceStoreId.value"
      :target-store-id="page.targetStoreId.value"
      :status-text="page.storesError.value ?? page.pageStatus.value"
      @update:reference-store="page.setReferenceStore"
      @update:target-store="page.setTargetStore"
    />

    <!-- ── Categories panel ─────────────────────────────────────── -->
    <section class="panel">
      <h2>Категорії</h2>
      <div class="grid-two">
        <div>
          <h3>Референс</h3>
          <ReferenceCategoryList
            :categories="page.referenceCategories.value"
            :active-category-id="page.referenceCategoryId.value"
            :loading="page.isLoadingRefCategories.value"
            @select="page.selectRefCategory"
          />
        </div>
        <div>
          <h3>Замаплені цільові категорії</h3>
          <MappedTargetCategoryList
            :mapped-targets="page.mappedTargets.value"
            :selected-ids="page.selectedTargetCategoryIds.value"
            :selected-category-id="page.referenceCategoryId.value"
            :loading="page.isLoadingMappedTargets.value"
            :no-mappings-warning="page.noMappingsWarning.value"
            @toggle="page.toggleTargetCategory"
          />
        </div>
      </div>
    </section>

    <!-- ── Comparison action ─────────────────────────────────────── -->
    <section class="panel">
      <h2>Порівняння</h2>
      <p class="panel-muted">
        Оберіть референсну категорію — замаплені цільові категорії з'являться автоматично.
      </p>
      <button
        id="compareBtn"
        class="btn"
        :disabled="!page.canCompare.value || page.isComparing.value"
        @click="page.compare"
      >
        {{ page.isComparing.value ? 'Виконується…' : 'Порівняти категорії' }}
      </button>

      <!-- Summary / status bar -->
      <ComparisonSummaryBar
        style="margin-top:14px;"
        :result="page.comparisonResult.value"
        :comparing="page.isComparing.value"
        :error-text="page.comparisonError.value ?? page.decisionError.value"
      />

      <!-- Results sections -->
      <div
        v-if="page.hasCompared.value && page.comparisonResult.value"
        class="comparison-sections"
        style="margin-top:20px;"
      >
        <!-- Auto suggestions -->
        <AutoSuggestionsTable
          v-if="page.autoSuggestions.value.length"
          :suggestions="page.autoSuggestions.value"
          :decision-in-progress-key="page.decisionInProgressKey.value"
          @decision="page.makeDecision"
        />

        <!-- Candidate groups -->
        <CandidateGroups
          v-if="page.comparisonResult.value.candidate_groups.length"
          :groups="page.comparisonResult.value.candidate_groups"
          :target-category-ids="Array.from(page.selectedTargetCategoryIds.value)"
          :decision-in-progress-key="page.decisionInProgressKey.value"
          @decision="page.makeDecision"
        />

        <!-- Reference-only + Target-only side by side -->
        <div class="grid-side-by-side">
          <ReferenceOnlySection
            :items="page.comparisonResult.value.reference_only"
            :target-category-ids="Array.from(page.selectedTargetCategoryIds.value)"
            @decision="page.makeDecision"
          />
          <TargetOnlySection
            :items="page.comparisonResult.value.target_only"
          />
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
/**
 * ComparisonPage.vue — root Vue component for the main comparison page (/).
 *
 * Mounted from frontend/src/entries/index.ts on #comparison-app.
 *
 * Owns all interactive UI via useComparisonPage:
 *   - store/category cascade loading
 *   - comparison execution
 *   - confirm/reject decisions
 *
 * Flask still owns: page shell (header/nav), CSS, <title>.
 */
import { onMounted } from 'vue'
import { useComparisonPage } from './composables/useComparisonPage'
import ComparisonFilters       from './components/ComparisonFilters.vue'
import ReferenceCategoryList   from './components/ReferenceCategoryList.vue'
import MappedTargetCategoryList from './components/MappedTargetCategoryList.vue'
import ComparisonSummaryBar    from './components/ComparisonSummaryBar.vue'
import AutoSuggestionsTable    from './components/AutoSuggestionsTable.vue'
import CandidateGroups         from './components/CandidateGroups.vue'
import ReferenceOnlySection    from './components/ReferenceOnlySection.vue'
import TargetOnlySection       from './components/TargetOnlySection.vue'

const page = useComparisonPage()

onMounted(() => {
  void page.loadStores()
})
</script>

