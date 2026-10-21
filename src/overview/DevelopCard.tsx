import { Icon } from '../components/Icon'
import { DEVELOP_PITCH } from './overview'
import './overview.css'

// The sidebar's Start developing entry while the highlight runs (DEVELOP_HIGHLIGHT_UNTIL in overview.ts).
export function DevelopCard({ current }: { current: boolean }) {
  return <a className={'develop-card' + (current ? ' active' : '')} href="#submit" aria-current={current ? 'page' : undefined}>
    <span className="develop-card-icon"><Icon name="plus" size={16} /></span>
    <strong>Start developing</strong>
    <small>{DEVELOP_PITCH}</small>
    <span className="develop-card-tag">Step by step</span>
  </a>
}
