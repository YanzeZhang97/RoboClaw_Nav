import { TERMINAL_ITEM_STATUSES, type DatasetJobItem, type RepairJobState } from '../types'
import type { JobEvent } from './sse'

function recomputeProcessed(items: DatasetJobItem[]): number {
  return items.filter((item) => TERMINAL_ITEM_STATUSES.has(item.status)).length
}

export function applyJobEvent(
  prev: RepairJobState | null,
  event: JobEvent,
): RepairJobState | null {
  if (event.type === 'snapshot' || event.type === 'complete') {
    return event.data as RepairJobState
  }
  if (event.type === 'error') {
    const payload = event.data as { job?: RepairJobState }
    return payload.job ?? prev
  }
  if (event.type === 'item') {
    if (!prev) return prev
    const incoming = event.data as DatasetJobItem
    const items = prev.items.map((item) =>
      item.dataset_id === incoming.dataset_id ? incoming : item,
    )
    if (!prev.items.some((item) => item.dataset_id === incoming.dataset_id)) {
      items.push(incoming)
    }
    return {
      ...prev,
      items,
      processed: recomputeProcessed(items),
    }
  }
  return prev
}
