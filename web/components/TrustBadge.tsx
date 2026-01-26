type Props = {
  label: string
  variant?: 'primary' | 'secondary' | 'accent'
}

const variantMap: Record<NonNullable<Props['variant']>, string> = {
  primary: 'bg-primary/10 text-primary border border-primary/30',
  secondary: 'bg-secondary/10 text-secondary border border-secondary/30',
  accent: 'bg-accent/10 text-accent border border-accent/30',
}

export default function TrustBadge({ label, variant = 'secondary' }: Props) {
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-bold ${variantMap[variant]}`}>
      {label}
    </span>
  )
}
