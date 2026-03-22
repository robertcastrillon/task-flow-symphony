interface StatCardProps {
  label: string;
  count: number;
  className?: string;
}

export default function StatCard({
  label,
  count,
  className = "",
}: StatCardProps) {
  return (
    <div className={`card bg-base-200 shadow-sm ${className}`}>
      <div className="card-body p-4">
        <p className="text-3xl font-bold">{count}</p>
        <p className="text-sm text-base-content/70">{label}</p>
      </div>
    </div>
  );
}
