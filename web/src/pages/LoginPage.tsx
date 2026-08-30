import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import SplitText from '../components/bits/SplitText'
import FadeContent from '../components/bits/FadeContent'
import SpotlightCard from '../components/bits/SpotlightCard'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'

export default function LoginPage() {
  const { setUser } = useAuth()
  const nav = useNavigate()
  const [username, setUsername] = useState('sale01')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { user } = await api.login(username)
      setUser(user)
      nav('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'เข้าสู่ระบบไม่สำเร็จ')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-ink text-paper">
      <div
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 20% 10%, rgba(146,100,42,.35), transparent), radial-gradient(ellipse 60% 40% at 90% 80%, rgba(35,80,73,.5), transparent)',
        }}
      />
      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col justify-center gap-10 px-5 py-12 lg:flex-row lg:items-end lg:gap-16">
        <div className="flex-1">
          <p className="font-display text-brass-soft mb-2 text-base italic">TranTech · SmartGift</p>
          <SplitText
            text="Price Boss"
            className="text-4xl font-bold tracking-tight md:text-6xl"
          />
          <FadeContent delay={0.35} className="mt-4 max-w-md text-sm leading-relaxed text-paper-3">
            โต๊ะทำงานราคาและใบเสนอราคา — เลือกบทบาท administrator / manager / sale
            เพื่อเข้าถึงข้อมูลตามสิทธิ์
          </FadeContent>
        </div>

        <FadeContent delay={0.2} className="w-full max-w-md">
          <SpotlightCard className="bg-paper! text-ink p-6">
            <h2 className="text-lg font-bold">เข้าสู่ระบบ</h2>
            <p className="mt-1 text-sm text-ink-3">ทดลอง: admin · manager · sale01</p>
            <form className="mt-5 space-y-4" onSubmit={onSubmit}>
              <label className="block text-sm text-ink-2">
                Username
                <input
                  className="mt-1.5 w-full rounded-[2px] border border-rule bg-field px-3 py-2 font-mono text-sm"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  required
                />
              </label>
              {error ? (
                <p className="rounded-[2px] bg-[#f3dcdc] px-3 py-2 text-sm text-crit" role="alert">
                  {error}
                </p>
              ) : null}
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-[2px] bg-ink px-4 py-2.5 text-sm font-semibold text-paper disabled:opacity-50"
              >
                {loading ? 'กำลังเข้า…' : 'เข้าโต๊ะราคา'}
              </button>
            </form>
          </SpotlightCard>
        </FadeContent>
      </div>
    </div>
  )
}
