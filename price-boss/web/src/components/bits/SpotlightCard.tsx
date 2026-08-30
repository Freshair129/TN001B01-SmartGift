import { useRef, type ReactNode, type MouseEvent } from 'react'

/** React Bits–style SpotlightCard */
type Props = {
  children: ReactNode
  className?: string
}

export default function SpotlightCard({ children, className = '' }: Props) {
  const ref = useRef<HTMLDivElement>(null)

  function onMove(e: MouseEvent) {
    const el = ref.current
    if (!el) return
    const r = el.getBoundingClientRect()
    el.style.setProperty('--mx', `${e.clientX - r.left}px`)
    el.style.setProperty('--my', `${e.clientY - r.top}px`)
  }

  return (
    <div
      ref={ref}
      onMouseMove={onMove}
      className={`relative overflow-hidden rounded-[3px] border border-rule bg-paper-2 shadow-[0_1px_2px_rgba(16,32,29,.07),0_8px_24px_-12px_rgba(16,32,29,.18)] ${className}`}
      style={{
        backgroundImage:
          'radial-gradient(420px circle at var(--mx, 50%) var(--my, 0%), rgba(146,100,42,.14), transparent 42%)',
      }}
    >
      {children}
    </div>
  )
}
