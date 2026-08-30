import { useEffect, useMemo, useState } from 'react'
import FadeContent from '../components/bits/FadeContent'
import SpotlightCard from '../components/bits/SpotlightCard'
import { api, type Employee, type Role, type RolePerm } from '../lib/api'
import { useAuth } from '../lib/auth'

export default function StaffPage() {
  const { can } = useAuth()
  const [emps, setEmps] = useState<Employee[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [perms, setPerms] = useState<RolePerm[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.employees(), api.roles()])
      .then(([e, r]) => {
        setEmps(e.rows)
        setRoles(r.roles)
        setPerms(r.permissions)
      })
      .catch((err) => setError(err.message))
  }, [])

  const byRole = useMemo(() => {
    const m = new Map<string, RolePerm[]>()
    for (const p of perms) {
      const list = m.get(p.role_code) || []
      list.push(p)
      m.set(p.role_code, list)
    }
    return m
  }, [perms])

  if (!can('employee.read') && !can('admin.access')) {
    return <p className="text-sm text-crit">ไม่มีสิทธิ์ดูหน้านี้</p>
  }

  return (
    <div>
      <FadeContent>
        <h2 className="text-2xl font-bold">พนักงาน / สิทธิ์</h2>
        <p className="mt-1 text-sm text-ink-3">administrator · manager · sale</p>
      </FadeContent>
      {error ? <p className="mt-3 text-sm text-crit">{error}</p> : null}

      <div className="mt-4 overflow-x-auto rounded-[3px] border border-rule">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="bg-paper-3 text-xs text-ink-3 uppercase">
            <tr>
              <th className="px-3 py-2">รหัส</th>
              <th className="px-3 py-2">ชื่อ</th>
              <th className="px-3 py-2">username</th>
              <th className="px-3 py-2">บทบาท</th>
              <th className="px-3 py-2">หัวหน้า</th>
            </tr>
          </thead>
          <tbody>
            {emps.map((e) => (
              <tr key={e.id} className="border-t border-rule">
                <td className="px-3 py-2 font-mono">{e.emp_code}</td>
                <td className="px-3 py-2">{e.full_name}</td>
                <td className="px-3 py-2 font-mono text-brass">{e.username}</td>
                <td className="px-3 py-2">{e.role_th}</td>
                <td className="px-3 py-2">{e.manager_name || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid gap-3 lg:grid-cols-3">
        {roles.map((r, i) => (
          <FadeContent key={r.code} delay={0.05 * i}>
            <SpotlightCard className="p-4">
              <p className="font-mono text-xs text-brass uppercase">{r.code}</p>
              <h3 className="mt-1 font-bold">{r.name_th}</h3>
              <p className="mt-1 text-xs text-ink-3">{r.description}</p>
              <ul className="mt-3 space-y-1 text-xs text-ink-2">
                {(byRole.get(r.code) || []).map((p) => (
                  <li key={p.permission_code} className="flex gap-2">
                    <span className="font-mono text-ink-3">{p.module}</span>
                    <span>{p.name_th}</span>
                  </li>
                ))}
              </ul>
            </SpotlightCard>
          </FadeContent>
        ))}
      </div>
    </div>
  )
}
