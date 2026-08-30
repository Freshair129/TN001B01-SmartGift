import type { ReactNode } from 'react'

type Col = { key: string; header: string; className?: string; mono?: boolean }

type Props<T extends { id: string | number }> = {
  columns: Col[]
  rows: T[]
  renderCell: (row: T, key: string) => ReactNode
  minWidth?: number
}

export default function DataTable<T extends { id: string | number }>({
  columns,
  rows,
  renderCell,
  minWidth = 720,
}: Props<T>) {
  return (
    <div className="overflow-x-auto rounded-[3px] border border-rule">
      <table className="w-full text-left text-sm" style={{ minWidth }}>
        <thead className="bg-paper-3 text-xs text-ink-3 uppercase">
          <tr>
            {columns.map((c) => (
              <th key={c.key} className={`px-3 py-2 ${c.className || ''}`}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} className="border-t border-rule align-top">
              {columns.map((c) => (
                <td
                  key={c.key}
                  className={`px-3 py-2.5 ${c.mono ? 'font-mono' : ''} ${c.className || ''}`}
                >
                  {renderCell(row, c.key)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
