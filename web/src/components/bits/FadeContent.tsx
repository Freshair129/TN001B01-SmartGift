import { motion, useReducedMotion } from 'framer-motion'
import type { ReactNode } from 'react'

/** React Bits–style FadeContent */
type Props = {
  children: ReactNode
  className?: string
  delay?: number
  y?: number
}

export default function FadeContent({ children, className = '', delay = 0, y = 12 }: Props) {
  const reduce = useReducedMotion()
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduce ? 0 : 0.45, delay: reduce ? 0 : delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}
