import { useMemo, useState } from 'react'
import FadeContent from '../components/bits/FadeContent'
import SpotlightCard from '../components/bits/SpotlightCard'
import schemaCatalog from '../data/schemaCatalog.json'
import workflows from '../data/workflows.json'

type TableRow = (typeof schemaCatalog.tables)[number]
type Flow = (typeof workflows.flows)[number]

const DOMAIN_ORDER = Object.entries(schemaCatalog.domains).sort(
  (a, b) => (a[1] as { order: number }).order - (b[1] as { order: number }).order,
)

function KeyBadge({ k }: { k: string }) {
  if (!k) return <span className="text-ink-3">—</span>
  const color =
    k === 'PRI'
      ? 'bg-ink text-paper'
      : k === 'UNI'
        ? 'bg-brass/20 text-brass'
        : k === 'MUL'
          ? 'bg-teal/15 text-teal'
          : 'bg-paper-3 text-ink-2'
  return (
    <span className={`rounded-[2px] px-1.5 py-0.5 font-mono text-[10px] font-semibold ${color}`}>
      {k}
    </span>
  )
}

export default function DocsPage() {
  const [tab, setTab] = useState<'dict' | 'flow'>('dict')
  const [domain, setDomain] = useState<string>('all')
  const [q, setQ] = useState('')
  const [tableName, setTableName] = useState<string | null>(null)
  const [flowId, setFlowId] = useState(workflows.flows[0]?.id || '')
  const [roleFilter, setRoleFilter] = useState<'all' | 'administrator' | 'manager' | 'sale'>('all')

  const tables = useMemo(() => {
    const qq = q.trim().toLowerCase()
    return schemaCatalog.tables.filter((t) => {
      if (domain !== 'all' && t.domain !== domain) return false
      if (!qq) return true
      const hay = [
        t.name,
        t.title_th,
        t.purpose,
        ...t.columns.map((c) => `${c.name} ${c.comment}`),
      ]
        .join(' ')
        .toLowerCase()
      return hay.includes(qq)
    })
  }, [domain, q])

  const selected: TableRow | null =
    (tableName && schemaCatalog.tables.find((t) => t.name === tableName)) ||
    tables[0] ||
    null

  const inbound = useMemo(() => {
    if (!selected) return []
    return schemaCatalog.tables.flatMap((t) =>
      t.foreign_keys
        .filter((fk) => fk.ref_table === selected.name)
        .map((fk) => ({ from: t.name, ...fk })),
    )
  }, [selected])

  const flow: Flow | undefined = workflows.flows.find((f) => f.id === flowId)

  const flowsFiltered = workflows.flows.filter(
    (f) => roleFilter === 'all' || f.actors.includes(roleFilter),
  )

  return (
    <div>
      <FadeContent>
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold">เอกสารระบบ</h2>
            <p className="mt-1 text-sm text-ink-3">
              Data Dictionary แบบ interactive + Workflow โดยละเอียด · DB{' '}
              <span className="font-mono text-brass">{schemaCatalog.database}</span> ·{' '}
              {schemaCatalog.tables.length} tables/views ·{' '}
              {schemaCatalog.tables.reduce((n, t) => n + t.columns.length, 0)} columns
            </p>
          </div>
          <div className="inline-flex rounded-[2px] border border-rule bg-field p-0.5" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'dict'}
              className={`rounded-[2px] px-3 py-1.5 text-sm font-semibold ${
                tab === 'dict' ? 'bg-ink text-paper' : 'text-ink-2'
              }`}
              onClick={() => setTab('dict')}
            >
              Data Dictionary
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'flow'}
              className={`rounded-[2px] px-3 py-1.5 text-sm font-semibold ${
                tab === 'flow' ? 'bg-ink text-paper' : 'text-ink-2'
              }`}
              onClick={() => setTab('flow')}
            >
              Workflow
            </button>
          </div>
        </div>
      </FadeContent>

      {tab === 'dict' ? (
        <div className="mt-5 grid gap-4 lg:grid-cols-[280px_1fr]">
          <SpotlightCard className="p-3 lg:max-h-[calc(100vh-8rem)] lg:overflow-hidden lg:flex lg:flex-col">
            <input
              className="w-full rounded-[2px] border border-rule bg-paper px-3 py-2 text-sm"
              placeholder="ค้นตาราง / คอลัมน์ / ความหมาย"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              aria-label="ค้น data dictionary"
            />
            <div className="mt-2 flex flex-wrap gap-1">
              <button
                type="button"
                onClick={() => setDomain('all')}
                className={`rounded-[2px] px-2 py-1 text-xs ${
                  domain === 'all' ? 'bg-ink text-paper' : 'bg-paper-3 text-ink-2'
                }`}
              >
                ทั้งหมด
              </button>
              {DOMAIN_ORDER.map(([key, meta]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setDomain(key)}
                  className={`rounded-[2px] px-2 py-1 text-xs ${
                    domain === key ? 'bg-ink text-paper' : 'bg-paper-3 text-ink-2'
                  }`}
                >
                  {(meta as { label: string }).label}
                </button>
              ))}
            </div>
            <ul className="mt-3 min-h-0 flex-1 space-y-0.5 overflow-y-auto pr-1" role="listbox">
              {tables.map((t) => (
                <li key={t.name}>
                  <button
                    type="button"
                    role="option"
                    aria-selected={selected?.name === t.name}
                    onClick={() => setTableName(t.name)}
                    className={`w-full rounded-[2px] px-2 py-1.5 text-left text-sm ${
                      selected?.name === t.name
                        ? 'bg-ink text-paper'
                        : 'hover:bg-paper-2 text-ink-2'
                    }`}
                  >
                    <span className="font-mono text-xs">{t.name}</span>
                    <span className="mt-0.5 block text-[11px] opacity-80">{t.title_th}</span>
                  </button>
                </li>
              ))}
              {!tables.length ? (
                <li className="px-2 py-4 text-sm text-ink-3">ไม่พบตารางตามคำค้น</li>
              ) : null}
            </ul>
          </SpotlightCard>

          {selected ? (
            <div className="min-w-0 space-y-4">
              <SpotlightCard className="p-5">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-mono text-xs text-brass uppercase">
                      {selected.kind} · {selected.domain}
                    </p>
                    <h3 className="mt-1 text-xl font-bold">
                      {selected.title_th}{' '}
                      <span className="font-mono text-base font-normal text-ink-3">
                        {selected.name}
                      </span>
                    </h3>
                    <p className="mt-2 text-sm text-ink-2">{selected.purpose || '—'}</p>
                  </div>
                  <p className="font-mono text-xs text-ink-3">
                    {selected.columns.length} cols · {selected.foreign_keys.length} FK out
                  </p>
                </div>

                {(selected.foreign_keys.length > 0 || inbound.length > 0) && (
                  <div className="mt-4 grid gap-3 md:grid-cols-2">
                    <div className="rounded-[2px] border border-rule bg-field p-3">
                      <p className="text-xs font-semibold tracking-wide text-ink-3 uppercase">
                        FK ออก (อ้างตารางอื่น)
                      </p>
                      <ul className="mt-2 space-y-1 text-sm">
                        {selected.foreign_keys.length ? (
                          selected.foreign_keys.map((fk) => (
                            <li key={`${fk.constraint}-${fk.column}`}>
                              <button
                                type="button"
                                className="font-mono text-brass hover:underline"
                                onClick={() => setTableName(fk.ref_table)}
                              >
                                {fk.column} → {fk.ref_table}.{fk.ref_column}
                              </button>
                            </li>
                          ))
                        ) : (
                          <li className="text-ink-3">ไม่มี</li>
                        )}
                      </ul>
                    </div>
                    <div className="rounded-[2px] border border-rule bg-field p-3">
                      <p className="text-xs font-semibold tracking-wide text-ink-3 uppercase">
                        ถูกอ้างโดย
                      </p>
                      <ul className="mt-2 space-y-1 text-sm">
                        {inbound.length ? (
                          inbound.map((fk) => (
                            <li key={`${fk.from}-${fk.constraint}-${fk.column}`}>
                              <button
                                type="button"
                                className="font-mono text-brass hover:underline"
                                onClick={() => setTableName(fk.from)}
                              >
                                {fk.from}.{fk.column}
                              </button>
                            </li>
                          ))
                        ) : (
                          <li className="text-ink-3">ไม่มีตารางอื่นชี้มา</li>
                        )}
                      </ul>
                    </div>
                  </div>
                )}
              </SpotlightCard>

              <div className="overflow-x-auto rounded-[3px] border border-rule">
                <table className="w-full min-w-[720px] text-left text-sm">
                  <thead className="bg-paper-3 text-xs tracking-wide text-ink-3 uppercase">
                    <tr>
                      <th className="px-3 py-2">#</th>
                      <th className="px-3 py-2">Column</th>
                      <th className="px-3 py-2">Type</th>
                      <th className="px-3 py-2">Null</th>
                      <th className="px-3 py-2">Key</th>
                      <th className="px-3 py-2">Default</th>
                      <th className="px-3 py-2">ความหมาย / หมายเหตุ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selected.columns.map((c) => (
                      <tr key={c.name} className="border-t border-rule align-top">
                        <td className="px-3 py-2 font-mono text-xs text-ink-3">{c.ordinal}</td>
                        <td className="px-3 py-2 font-mono text-brass">{c.name}</td>
                        <td className="px-3 py-2 font-mono text-xs">{c.type}</td>
                        <td className="px-3 py-2">{c.nullable ? 'YES' : 'NO'}</td>
                        <td className="px-3 py-2">
                          <KeyBadge k={c.key} />
                        </td>
                        <td className="px-3 py-2 font-mono text-xs text-ink-3">
                          {c.default == null || c.default === '' ? '—' : String(c.default)}
                          {c.extra ? ` · ${c.extra}` : ''}
                        </td>
                        <td className="px-3 py-2 text-ink-2">{c.comment || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
        </div>
      ) : (
        <div className="mt-5 grid gap-4 lg:grid-cols-[260px_1fr]">
          <SpotlightCard className="p-3">
            <label className="block text-xs text-ink-3">กรองตามบทบาท</label>
            <select
              className="mt-1 w-full rounded-[2px] border border-rule bg-paper px-2 py-2 text-sm"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as typeof roleFilter)}
            >
              <option value="all">ทุกบทบาท</option>
              <option value="sale">sale</option>
              <option value="manager">manager</option>
              <option value="administrator">administrator</option>
            </select>
            <ul className="mt-3 space-y-1">
              {flowsFiltered.map((f) => (
                <li key={f.id}>
                  <button
                    type="button"
                    onClick={() => setFlowId(f.id)}
                    className={`w-full rounded-[2px] px-2 py-2 text-left text-sm ${
                      flowId === f.id ? 'bg-ink text-paper' : 'hover:bg-paper-2 text-ink-2'
                    }`}
                  >
                    <span className="font-semibold">{f.title}</span>
                    <span className="mt-0.5 block text-[11px] opacity-80">{f.domain}</span>
                  </button>
                </li>
              ))}
            </ul>
          </SpotlightCard>

          {flow ? (
            <div className="min-w-0 space-y-4">
              <SpotlightCard className="p-5">
                <p className="font-mono text-xs text-brass uppercase">{flow.domain}</p>
                <h3 className="mt-1 text-xl font-bold">{flow.title}</h3>
                <p className="mt-2 text-sm text-ink-2">{flow.summary}</p>
                <p className="mt-3 text-xs text-ink-3">
                  Actors:{' '}
                  <span className="font-mono text-ink-2">{flow.actors.join(' · ')}</span>
                </p>
                {'diagram' in flow && Array.isArray(flow.diagram) && flow.diagram.length ? (
                  <pre className="mt-4 overflow-x-auto rounded-[2px] border border-rule bg-field p-3 font-mono text-[11px] leading-relaxed text-ink-2">
                    {flow.diagram.join('\n')}
                  </pre>
                ) : null}
              </SpotlightCard>

              {'transitions' in flow && Array.isArray(flow.transitions) && flow.transitions.length ? (
                <div className="overflow-x-auto rounded-[3px] border border-rule">
                  <table className="w-full min-w-[640px] text-left text-sm">
                    <thead className="bg-paper-3 text-xs text-ink-3 uppercase">
                      <tr>
                        <th className="px-3 py-2">From</th>
                        <th className="px-3 py-2">Action</th>
                        <th className="px-3 py-2">To</th>
                        <th className="px-3 py-2">Who</th>
                        <th className="px-3 py-2">Permission</th>
                      </tr>
                    </thead>
                    <tbody>
                      {flow.transitions.map((tr, i) => (
                        <tr key={i} className="border-t border-rule">
                          <td className="px-3 py-2 font-mono text-xs">{tr.from}</td>
                          <td className="px-3 py-2">{tr.action}</td>
                          <td className="px-3 py-2 font-mono text-xs text-brass">{tr.to}</td>
                          <td className="px-3 py-2 text-ink-2">{tr.who}</td>
                          <td className="px-3 py-2 font-mono text-xs">{tr.perm}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}

              <ol className="space-y-3">
                {flow.steps.map((s) => (
                  <li key={s.n}>
                    <SpotlightCard className="p-4">
                      <div className="flex flex-wrap items-baseline gap-2">
                        <span className="font-mono text-brass">Step {s.n}</span>
                        <h4 className="font-semibold">{s.action}</h4>
                      </div>
                      <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
                        <div>
                          <dt className="text-xs text-ink-3">ผู้ทำ</dt>
                          <dd>{s.actor}</dd>
                        </div>
                        <div>
                          <dt className="text-xs text-ink-3">ระบบ / API</dt>
                          <dd className="font-mono text-xs">{s.system}</dd>
                        </div>
                        <div className="sm:col-span-2">
                          <dt className="text-xs text-ink-3">ตารางที่เกี่ยวข้อง</dt>
                          <dd className="mt-1 flex flex-wrap gap-1">
                            {s.tables.length ? (
                              s.tables.map((t) => (
                                <button
                                  key={t}
                                  type="button"
                                  className="rounded-[2px] border border-rule bg-field px-2 py-0.5 font-mono text-[11px] text-brass hover:bg-paper-2"
                                  onClick={() => {
                                    setTab('dict')
                                    setTableName(t)
                                    setDomain('all')
                                  }}
                                >
                                  {t}
                                </button>
                              ))
                            ) : (
                              <span className="text-ink-3">—</span>
                            )}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-xs text-ink-3">Pre-conditions</dt>
                          <dd>
                            <ul className="mt-1 list-disc space-y-0.5 pl-4 text-ink-2">
                              {s.pre.map((p) => (
                                <li key={p}>{p}</li>
                              ))}
                            </ul>
                          </dd>
                        </div>
                        <div>
                          <dt className="text-xs text-ink-3">Post-conditions</dt>
                          <dd>
                            <ul className="mt-1 list-disc space-y-0.5 pl-4 text-ink-2">
                              {s.post.map((p) => (
                                <li key={p}>{p}</li>
                              ))}
                            </ul>
                          </dd>
                        </div>
                        {s.fail.length ? (
                          <div className="sm:col-span-2">
                            <dt className="text-xs text-crit">Fail cases</dt>
                            <dd>
                              <ul className="mt-1 list-disc space-y-0.5 pl-4 text-ink-2">
                                {s.fail.map((p) => (
                                  <li key={p}>{p}</li>
                                ))}
                              </ul>
                            </dd>
                          </div>
                        ) : null}
                      </dl>
                    </SpotlightCard>
                  </li>
                ))}
              </ol>

              {flow.notes?.length ? (
                <SpotlightCard className="p-4">
                  <h4 className="text-sm font-semibold">หมายเหตุ</h4>
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-2">
                    {flow.notes.map((n) => (
                      <li key={n}>{n}</li>
                    ))}
                  </ul>
                </SpotlightCard>
              ) : null}

              <SpotlightCard className="p-5">
                <h4 className="text-sm font-semibold">Permission matrix</h4>
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full min-w-[480px] text-left text-sm">
                    <thead className="text-xs text-ink-3 uppercase">
                      <tr>
                        <th className="py-1.5 pr-2">code</th>
                        <th className="py-1.5 pr-2">admin</th>
                        <th className="py-1.5 pr-2">manager</th>
                        <th className="py-1.5">sale</th>
                      </tr>
                    </thead>
                    <tbody>
                      {workflows.permissions_matrix.map((p) => (
                        <tr key={p.code} className="border-t border-rule">
                          <td className="py-1.5 pr-2 font-mono text-xs">{p.code}</td>
                          <td className="py-1.5 pr-2">{p.admin ? 'Y' : '—'}</td>
                          <td className="py-1.5 pr-2">{p.manager ? 'Y' : '—'}</td>
                          <td className="py-1.5">{p.sale ? 'Y' : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </SpotlightCard>

              <SpotlightCard className="p-5">
                <h4 className="text-sm font-semibold">Checklist ฟิลด์ตามสถานะใบเสนอราคา</h4>
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full min-w-[520px] text-left text-sm">
                    <thead className="text-xs text-ink-3 uppercase">
                      <tr>
                        <th className="py-1.5 pr-2">สถานะ</th>
                        <th className="py-1.5 pr-2">หัวใบ</th>
                        <th className="py-1.5">รายการ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {workflows.field_checklist.map((r) => (
                        <tr key={r.status} className="border-t border-rule align-top">
                          <td className="py-2 pr-2 font-mono text-xs text-brass">{r.status}</td>
                          <td className="py-2 pr-2 text-ink-2">{r.header.join(', ')}</td>
                          <td className="py-2 text-ink-2">{r.lines}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </SpotlightCard>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}
