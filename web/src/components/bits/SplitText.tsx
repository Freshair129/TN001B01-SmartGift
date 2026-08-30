import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'

/** React Bits–style SplitText (TS + Tailwind), adapted for Price Boss */
type Props = {
  text: string
  className?: string
  delay?: number
  duration?: number
  stagger?: number
}

export default function SplitText({
  text,
  className = '',
  delay = 0,
  duration = 0.55,
  stagger = 0.035,
}: Props) {
  const ref = useRef<HTMLParagraphElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const chars = el.querySelectorAll<HTMLElement>('[data-char]')
    if (reduce) {
      gsap.set(chars, { opacity: 1, y: 0 })
      return
    }
    const tween = gsap.fromTo(
      chars,
      { opacity: 0, y: 18 },
      { opacity: 1, y: 0, duration, delay, stagger, ease: 'power3.out' },
    )
    return () => {
      tween.kill()
    }
  }, [text, delay, duration, stagger])

  return (
    <p ref={ref} className={className} aria-label={text}>
      {Array.from(text).map((ch, i) => (
        <span key={`${ch}-${i}`} data-char className="inline-block whitespace-pre">
          {ch}
        </span>
      ))}
    </p>
  )
}
