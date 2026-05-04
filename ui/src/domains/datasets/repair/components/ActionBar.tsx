import { ActionButton } from '@/shared/ui'

interface ActionBarProps {
  hasDatasets: boolean
  isJobActive: boolean
  acting: boolean
  onDiagnose: () => void
  onCancel: () => void
}

export default function ActionBar({
  hasDatasets,
  isJobActive,
  acting,
  onDiagnose,
  onCancel,
}: ActionBarProps) {
  const diagnoseDisabled = !hasDatasets || isJobActive || acting
  const cancelDisabled = !isJobActive || acting
  return (
    <div className="flex flex-wrap items-center gap-3">
      <ActionButton
        variant="primary"
        onClick={onDiagnose}
        disabled={diagnoseDisabled}
      >
        开始诊断
      </ActionButton>
      <ActionButton
        variant="secondary"
        disabled
        title="Phase 3 启用"
      >
        一键修复
      </ActionButton>
      <ActionButton
        variant="warning"
        onClick={onCancel}
        disabled={cancelDisabled}
      >
        取消
      </ActionButton>
      {!hasDatasets && (
        <span className="text-xs text-tx2">先扫描得到数据集才能开始诊断</span>
      )}
    </div>
  )
}
