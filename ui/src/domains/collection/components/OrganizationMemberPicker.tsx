import { useMemo, useState } from 'react'
import { type OrganizationMember } from '@/shared/api/evoClient'
import { cn } from '@/shared/lib/cn'

const PHONE_PATTERN = /^1\d{10}$/
const MAX_SUGGESTIONS = 6

function normalized(value: string) {
  return value.trim().toLowerCase()
}

function memberMatches(member: OrganizationMember, query: string) {
  const needle = normalized(query)
  if (!needle) return false
  return member.phone.includes(needle) || normalized(member.nickname || '').includes(needle)
}

function memberLabel(member: OrganizationMember) {
  return member.nickname?.trim() || member.phone
}

export function resolveOrganizationMemberInput(value: string, members: OrganizationMember[]) {
  const query = value.trim()
  if (PHONE_PATTERN.test(query)) return query
  return resolveOrganizationMemberSelection(query, members)
}

export function resolveOrganizationMemberSelection(value: string, members: OrganizationMember[]) {
  const query = value.trim()
  const exactMatches = members.filter((member) => (
    normalized(member.nickname || '') === normalized(query) || member.phone === query
  ))
  return exactMatches.length === 1 ? exactMatches[0].phone : null
}

interface OrganizationMemberPickerProps {
  value: string
  members: OrganizationMember[]
  onChange: (value: string) => void
  disabled?: boolean
  inputClassName?: string
  placeholder?: string
  required?: boolean
}

export default function OrganizationMemberPicker({
  value,
  members,
  onChange,
  disabled = false,
  inputClassName,
  placeholder = '输入手机号或昵称',
  required = false,
}: OrganizationMemberPickerProps) {
  const [focused, setFocused] = useState(false)
  const suggestions = useMemo(
    () => members.filter((member) => memberMatches(member, value)).slice(0, MAX_SUGGESTIONS),
    [members, value],
  )
  const showSuggestions = focused && value.trim().length > 0 && suggestions.length > 0

  function chooseMember(member: OrganizationMember) {
    onChange(member.phone)
    setFocused(false)
  }

  return (
    <div className="collection-member-picker">
      <input
        className={cn('collection-input', inputClassName)}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        aria-autocomplete="list"
      />
      {showSuggestions && (
        <div className="collection-member-picker__menu" role="listbox">
          {suggestions.map((member) => (
            <button
              key={member.id}
              className="collection-member-picker__option"
              type="button"
              role="option"
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => chooseMember(member)}
            >
              <span>
                <strong>{memberLabel(member)}</strong>
                {member.nickname && <small>{member.phone}</small>}
              </span>
              <i>{member.role_code}</i>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
