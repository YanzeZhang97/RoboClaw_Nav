import { jobEventsUrl } from './api'

export type JobEventType = 'snapshot' | 'item' | 'complete' | 'error'

export interface JobEvent {
  type: JobEventType
  data: any
}

const NAMED_EVENTS: JobEventType[] = ['snapshot', 'item', 'complete', 'error']

export function subscribeJobEvents(
  jobId: string,
  onEvent: (event: JobEvent) => void,
  onClose: () => void,
): () => void {
  const source = new EventSource(jobEventsUrl(jobId))
  let closed = false

  function close(): void {
    if (closed) return
    closed = true
    source.close()
    onClose()
  }

  function handleNamed(type: JobEventType, raw: MessageEvent): void {
    let parsed: unknown
    try {
      parsed = JSON.parse(raw.data)
    } catch (err) {
      onEvent({ type: 'error', data: { error: `Invalid SSE payload: ${String(err)}` } })
      close()
      return
    }
    onEvent({ type, data: parsed })
    if (type === 'complete' || type === 'error') {
      close()
    }
  }

  for (const type of NAMED_EVENTS) {
    source.addEventListener(type, (event) => handleNamed(type, event as MessageEvent))
  }

  source.onerror = () => {
    if (source.readyState === EventSource.CLOSED) {
      close()
    }
  }

  return close
}
