import { create } from 'zustand'
import {
  cancelJob,
  getCurrentJob,
  listDatasets,
  startDiagnose,
} from '../lib/api'
import { applyJobEvent } from '../lib/reducer'
import { subscribeJobEvents } from '../lib/sse'
import {
  TERMINAL_PHASES,
  type DatasetRepairDataset,
  type DatasetRepairFilters,
  type RepairJobState,
} from '../types'

const DEFAULT_FILTERS: DatasetRepairFilters = {
  root: '',
  date_from: '',
  date_to: '',
  task: '',
  tag: 'all',
}

interface DatasetRepairStore {
  filters: DatasetRepairFilters
  datasets: DatasetRepairDataset[]
  effectiveRoot: string
  loading: boolean
  acting: boolean
  error: string
  currentJob: RepairJobState | null
  unsubscribe: (() => void) | null

  setFilter: <K extends keyof DatasetRepairFilters>(
    key: K,
    value: DatasetRepairFilters[K],
  ) => void
  resetError: () => void
  loadDatasets: () => Promise<void>
  refreshCurrentJob: () => Promise<void>
  startDiagnosis: () => Promise<void>
  subscribeToJob: (jobId: string) => void
  cancelCurrent: () => Promise<void>
  teardown: () => void
}

function isJobActive(job: RepairJobState | null): boolean {
  return job !== null && !TERMINAL_PHASES.has(job.phase)
}

export const useDatasetRepairStore = create<DatasetRepairStore>((set, get) => ({
  filters: { ...DEFAULT_FILTERS },
  datasets: [],
  effectiveRoot: '',
  loading: false,
  acting: false,
  error: '',
  currentJob: null,
  unsubscribe: null,

  setFilter: (key, value) => {
    set((state) => ({ filters: { ...state.filters, [key]: value } }))
  },

  resetError: () => set({ error: '' }),

  loadDatasets: async () => {
    set({ loading: true, error: '' })
    try {
      const response = await listDatasets(get().filters)
      set({ datasets: response.datasets, effectiveRoot: response.root })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '加载数据集失败' })
    } finally {
      set({ loading: false })
    }
  },

  refreshCurrentJob: async () => {
    try {
      const { job } = await getCurrentJob()
      set({ currentJob: job })
      if (job && isJobActive(job)) {
        get().subscribeToJob(job.job_id)
      }
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '获取任务状态失败' })
    }
  },

  startDiagnosis: async () => {
    if (get().acting) return
    set({ acting: true, error: '' })
    try {
      const job = await startDiagnose(get().filters)
      set({ currentJob: job })
      get().subscribeToJob(job.job_id)
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '启动诊断失败' })
      throw error
    } finally {
      set({ acting: false })
    }
  },

  subscribeToJob: (jobId) => {
    const previous = get().unsubscribe
    if (previous) previous()
    const close = subscribeJobEvents(
      jobId,
      (event) => {
        set((state) => ({ currentJob: applyJobEvent(state.currentJob, event) }))
        if (event.type === 'error') {
          const payload = event.data as { error?: string }
          if (payload.error) set({ error: payload.error })
        }
      },
      () => {
        set({ unsubscribe: null })
        // After SSE closes, refresh dataset list so tags/repairable reflect the result.
        void get().loadDatasets()
      },
    )
    set({ unsubscribe: close })
  },

  cancelCurrent: async () => {
    const job = get().currentJob
    if (!job) return
    set({ acting: true, error: '' })
    try {
      const next = await cancelJob(job.job_id)
      set({ currentJob: next })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '取消失败' })
      throw error
    } finally {
      set({ acting: false })
    }
  },

  teardown: () => {
    const close = get().unsubscribe
    if (close) close()
    set({ unsubscribe: null })
  },
}))

export function selectIsJobActive(state: DatasetRepairStore): boolean {
  return isJobActive(state.currentJob)
}
