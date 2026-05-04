import { api, postJson } from '@/shared/api/client'
import type {
  DatasetRepairFilters,
  ListDatasetsResponse,
  RepairJobState,
} from '../types'

const BASE = '/api/dataset-repair'

function buildListUrl(filters: DatasetRepairFilters): string {
  const params = new URLSearchParams()
  if (filters.root.trim()) params.set('root', filters.root.trim())
  if (filters.date_from.trim()) params.set('date_from', filters.date_from.trim())
  if (filters.date_to.trim()) params.set('date_to', filters.date_to.trim())
  if (filters.task.trim()) params.set('task', filters.task.trim())
  if (filters.tag !== 'all') params.set('tag', filters.tag)
  const qs = params.toString()
  return qs ? `${BASE}/datasets?${qs}` : `${BASE}/datasets`
}

export function listDatasets(filters: DatasetRepairFilters): Promise<ListDatasetsResponse> {
  return api<ListDatasetsResponse>(buildListUrl(filters))
}

export function startDiagnose(
  filters: DatasetRepairFilters,
  datasetIds?: string[],
): Promise<RepairJobState> {
  const body: Record<string, unknown> = {
    filters: {
      root: filters.root.trim() || null,
      date_from: filters.date_from.trim() || null,
      date_to: filters.date_to.trim() || null,
      task: filters.task.trim() || null,
      tag: filters.tag,
    },
  }
  if (datasetIds && datasetIds.length > 0) {
    body.dataset_ids = datasetIds
  }
  return postJson<RepairJobState>(`${BASE}/diagnose`, body)
}

export function getCurrentJob(): Promise<{ job: RepairJobState | null }> {
  return api<{ job: RepairJobState | null }>(`${BASE}/jobs/current`)
}

export function getJob(jobId: string): Promise<RepairJobState> {
  return api<RepairJobState>(`${BASE}/jobs/${encodeURIComponent(jobId)}`)
}

export function cancelJob(jobId: string): Promise<RepairJobState> {
  return postJson<RepairJobState>(`${BASE}/jobs/${encodeURIComponent(jobId)}/cancel`)
}

export function jobEventsUrl(jobId: string): string {
  return `${BASE}/jobs/${encodeURIComponent(jobId)}/events`
}
