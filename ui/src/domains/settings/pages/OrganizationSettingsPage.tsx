import { FormEvent, useEffect, useState } from 'react'
import SettingsPageFrame from '@/domains/settings/components/SettingsPageFrame'
import {
    canManageOrganization,
    evoApi,
    type CurrentOrganization,
    type MembershipRole,
    type OrganizationMember,
} from '@/shared/api/evoClient'
import { useAuthStore } from '@/shared/lib/authStore'
import { useI18n } from '@/i18n'

const roleOptions: MembershipRole[] = ['owner', 'admin', 'member']

function maskPhone(phone: string): string {
    if (phone.length !== 11) return phone
    return `${phone.slice(0, 3)}****${phone.slice(7)}`
}

function roleLabel(role: MembershipRole): string {
    if (role === 'owner') return 'Owner'
    if (role === 'admin') return 'Admin'
    return 'Member'
}

export default function OrganizationSettingsPage() {
    const { t } = useI18n()
    const user = useAuthStore((state) => state.user)
    const [organization, setOrganization] = useState<CurrentOrganization | null>(null)
    const [phone, setPhone] = useState('')
    const [roleCode, setRoleCode] = useState<MembershipRole>('member')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [notice, setNotice] = useState('')

    const canEdit = canManageOrganization(user)

    async function loadOrganization() {
        setError('')
        try {
            setOrganization(await evoApi.getCurrentOrganization())
        } catch (err) {
            setOrganization(null)
            setError(err instanceof Error ? err.message : String(err))
        }
    }

    useEffect(() => {
        void loadOrganization()
    }, [])

    async function addMember(event: FormEvent) {
        event.preventDefault()
        setLoading(true)
        setError('')
        setNotice('')
        try {
            await evoApi.upsertOrganizationMember(phone, roleCode)
            setPhone('')
            setRoleCode('member')
            setNotice(t('organizationMemberSaved'))
            await loadOrganization()
        } catch (err) {
            setError(err instanceof Error ? err.message : String(err))
        } finally {
            setLoading(false)
        }
    }

    async function updateMember(member: OrganizationMember, payload: { role_code?: MembershipRole; status?: 'active' | 'disabled' }) {
        setLoading(true)
        setError('')
        setNotice('')
        try {
            await evoApi.updateOrganizationMember(member.id, payload)
            setNotice(t('organizationMemberSaved'))
            await loadOrganization()
        } catch (err) {
            setError(err instanceof Error ? err.message : String(err))
        } finally {
            setLoading(false)
        }
    }

    return (
        <SettingsPageFrame title={t('organizationSettingsTitle')} description={t('organizationSettingsDesc')}>
            <div className="mx-auto max-w-4xl space-y-5">
                {error && (
                    <div className="rounded-xl border border-rd/25 bg-rd/10 px-4 py-3 text-sm text-rd">
                        {error}
                    </div>
                )}
                {notice && (
                    <div className="rounded-xl border border-gn/25 bg-gn/10 px-4 py-3 text-sm text-gn">
                        {notice}
                    </div>
                )}

                <section className="glass-panel p-5">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--tx2)]">
                                {t('organizationName')}
                            </div>
                            <h3 className="mt-1 text-xl font-semibold text-[color:var(--tx)]">
                                {organization?.name || '-'}
                            </h3>
                        </div>
                        <span className="inline-flex w-fit rounded-full bg-[rgba(47,111,228,0.12)] px-3 py-1 text-sm font-semibold text-[color:var(--ac)]">
                            {organization ? roleLabel(organization.role_code) : '-'}
                        </span>
                    </div>
                </section>

                {canEdit && (
                    <form className="glass-panel grid gap-3 p-5 sm:grid-cols-[1fr_160px_auto]" onSubmit={addMember}>
                        <input
                            className="rounded-xl border border-[color:var(--bd)] bg-[color:var(--bg)] px-4 py-2.5 text-sm outline-none focus:border-[color:var(--ac)]"
                            value={phone}
                            onChange={(event) => setPhone(event.target.value)}
                            placeholder={t('organizationMemberPhone')}
                            maxLength={11}
                        />
                        <select
                            className="rounded-xl border border-[color:var(--bd)] bg-[color:var(--bg)] px-4 py-2.5 text-sm outline-none focus:border-[color:var(--ac)]"
                            value={roleCode}
                            onChange={(event) => setRoleCode(event.target.value as MembershipRole)}
                        >
                            {roleOptions.map((role) => (
                                <option key={role} value={role}>{roleLabel(role)}</option>
                            ))}
                        </select>
                        <button
                            className="rounded-xl bg-[color:var(--ac)] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
                            type="submit"
                            disabled={loading || phone.length !== 11}
                        >
                            {t('organizationMemberAdd')}
                        </button>
                    </form>
                )}

                <section className="glass-panel overflow-hidden">
                    <div className="hidden gap-3 border-b border-[color:var(--bd)]/60 px-5 py-3 text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--tx2)] md:grid md:grid-cols-[1.2fr_1fr_120px_130px]">
                        <span>{t('accountPhone')}</span>
                        <span>{t('accountNickname')}</span>
                        <span>{t('organizationRole')}</span>
                        <span>{t('organizationStatus')}</span>
                    </div>
                    {(organization?.members || []).map((member) => (
                        <div
                            key={member.id}
                            className="grid grid-cols-1 items-center gap-3 border-b border-[color:var(--bd)]/40 px-5 py-4 last:border-b-0 md:grid-cols-[1.2fr_1fr_120px_130px] md:py-3"
                        >
                            <span className="text-sm font-medium text-[color:var(--tx)]">{maskPhone(member.phone)}</span>
                            <span className="truncate text-sm text-[color:var(--tx2)]">{member.nickname || '-'}</span>
                            {canEdit ? (
                                <select
                                    className="rounded-lg border border-[color:var(--bd)] bg-white px-2 py-1.5 text-sm"
                                    value={member.role_code}
                                    disabled={loading}
                                    onChange={(event) => void updateMember(member, { role_code: event.target.value as MembershipRole })}
                                >
                                    {roleOptions.map((role) => (
                                        <option key={role} value={role}>{roleLabel(role)}</option>
                                    ))}
                                </select>
                            ) : (
                                <span className="text-sm text-[color:var(--tx)]">{roleLabel(member.role_code)}</span>
                            )}
                            {canEdit ? (
                                <select
                                    className="rounded-lg border border-[color:var(--bd)] bg-white px-2 py-1.5 text-sm"
                                    value={member.status}
                                    disabled={loading}
                                    onChange={(event) => void updateMember(member, { status: event.target.value as 'active' | 'disabled' })}
                                >
                                    <option value="active">active</option>
                                    <option value="disabled">disabled</option>
                                </select>
                            ) : (
                                <span className="text-sm text-[color:var(--tx2)]">{member.status}</span>
                            )}
                        </div>
                    ))}
                </section>
            </div>
        </SettingsPageFrame>
    )
}
