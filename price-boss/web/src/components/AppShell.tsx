import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  Package,
  Users,
  FileText,
  Shield,
  LogOut,
  Target,
  BarChart3,
  BookOpen,
} from 'lucide-react'
import { useAuth } from '../lib/auth'

const links = [
  { to: '/', label: 'ภาพรวม', icon: LayoutDashboard, perm: null },
  { to: '/offers', label: 'สินค้า / ราคา', icon: Package, perm: 'product.read' },
  { to: '/report', label: 'รายงาน SmartGift', icon: BarChart3, perm: 'product.read' },
  { to: '/sales-command', label: 'Quota & แผน', icon: Target, perm: 'product.read' },
  { to: '/docs', label: 'เอกสาร / DataDict', icon: BookOpen, perm: null },
  { to: '/customers', label: 'ลูกค้า', icon: Users, perm: 'customer.read' },
  { to: '/quotations', label: 'ใบเสนอราคา', icon: FileText, perm: 'quote.read' },
  { to: '/staff', label: 'พนักงาน / สิทธิ์', icon: Shield, perm: 'employee.read' },
]

export default function AppShell() {
  const { user, logout, can } = useAuth()
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[240px_1fr]">
      <aside className="flex flex-col border-b border-rule bg-paper-3 lg:min-h-screen lg:border-b-0 lg:border-r">
        <div className="border-b-2 border-ink px-4 py-5">
          <p className="font-display text-sm italic text-brass">SmartGift · Price Boss</p>
          <h1 className="text-lg font-bold tracking-tight text-ink">โต๊ะราคา</h1>
        </div>
        <nav className="flex gap-1 overflow-x-auto p-3 lg:flex-1 lg:flex-col" aria-label="หลัก">
          {links
            .filter((l) => !l.perm || can(l.perm))
            .map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-[2px] px-3 py-2 text-sm whitespace-nowrap ${
                    isActive
                      ? 'bg-ink text-paper font-semibold'
                      : 'text-ink-2 hover:bg-paper-2'
                  }`
                }
              >
                <l.icon size={16} aria-hidden />
                {l.label}
              </NavLink>
            ))}
        </nav>
        <div className="flex items-center justify-between gap-3 border-t border-rule p-3 lg:mt-auto lg:block lg:p-4">
          <div className="min-w-0">
            <p className="hidden text-xs text-ink-3 lg:block">เข้าสู่ระบบเป็น</p>
            <p className="truncate text-sm font-semibold">{user?.fullName}</p>
            <p className="text-xs text-brass">{user?.roleTh}</p>
          </div>
          <button
            type="button"
            onClick={logout}
            className="inline-flex shrink-0 items-center gap-1.5 rounded-[2px] border border-rule px-2.5 py-1.5 text-sm text-ink-2 hover:border-crit hover:text-crit"
          >
            <LogOut size={14} /> ออก
          </button>
        </div>
      </aside>
      <main className="min-w-0 p-4 md:p-6 lg:p-8">
        <Outlet />
      </main>
    </div>
  )
}
