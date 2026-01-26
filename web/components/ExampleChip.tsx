type Props = {
  label: string
  onClick?: (label: string) => void
}

export default function ExampleChip({ label, onClick }: Props) {
  return (
    <button
      type="button"
      onClick={() => onClick?.(label)}
      className="inline-flex items-center rounded-xl bg-card px-3 py-1.5 text-sm font-semibold shadow-md hover:shadow-lg hover:bg-bg border border-secondary transition focus:outline-none focus:ring-2 focus:ring-secondary focus:ring-offset-2"
    >
      {label}
    </button>
  )
}
