type Props = {
  icon: React.ReactNode
  title: string
  description: string
  className?: string
}

export default function FeatureCard({ icon, title, description, className }: Props) {
  return (
    <div
      className={`rounded-xl border bg-card p-5 shadow-mdx card-hover ${className ?? ''}`}
      style={{ backgroundImage: 'radial-gradient(1200px circle at 0% 0%, rgba(58,158,158,0.08), transparent 40%), radial-gradient(800px circle at 100% 100%, rgba(10,36,99,0.06), transparent 42%)' }}
    >
      <div className="text-2xl">{icon}</div>
      <div className="mt-3 text-lg font-extrabold">{title}</div>
      <div className="mt-1 text-sm text-text/80">{description}</div>
    </div>
  )
}
