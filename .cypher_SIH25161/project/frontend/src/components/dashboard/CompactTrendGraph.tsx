import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from 'recharts';
import type { TrendPoint } from '@/lib/threat-utils';

interface CompactTrendGraphProps {
  data: TrendPoint[];
}

const CompactTrendGraph = ({ data }: CompactTrendGraphProps) => {
  return (
    <div className="glass-card p-4 h-full">
      <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-2">
        Risk Trend
      </h3>
      
      <div className="h-36">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="compactTrendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="time"
              tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 8, fontFamily: 'JetBrains Mono' }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              hide
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="hsl(var(--chart-1))"
              strokeWidth={1.5}
              fill="url(#compactTrendGradient)"
              animationDuration={600}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CompactTrendGraph;