import type { TrendPoint } from '@/lib/threat-utils';

interface ActivityLogProps {
  data: TrendPoint[];
}

const ActivityLog = ({ data }: ActivityLogProps) => {
  const getScoreColor = (value: number) => {
    if (value <= 25) return 'text-success';
    if (value <= 50) return 'text-chart-1';
    if (value <= 75) return 'text-warning';
    return 'text-danger';
  };

  const getDotColor = (value: number) => {
    if (value <= 25) return 'bg-success';
    if (value <= 50) return 'bg-chart-1';
    if (value <= 75) return 'bg-warning';
    return 'bg-danger';
  };

  return (
    <div className="glass-card p-4 h-full">
      <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-3">
        Activity Log
      </h3>
      
      <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
        {data.length > 0 ? (
          [...data].reverse().map((point, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 rounded-md bg-secondary/30 border border-border/30"
            >
              <div className="flex items-center gap-2">
                <div className={`h-1.5 w-1.5 rounded-full ${getDotColor(point.value)}`} />
                <span className="font-mono-display text-[10px] text-muted-foreground">
                  {point.time}
                </span>
              </div>
              <span className={`font-mono-display text-xs font-semibold ${getScoreColor(point.value)}`}>
                {point.value}%
              </span>
            </div>
          ))
        ) : (
          <p className="font-mono-display text-[10px] text-muted-foreground text-center py-4">
            No activity recorded
          </p>
        )}
      </div>
    </div>
  );
};

export default ActivityLog;