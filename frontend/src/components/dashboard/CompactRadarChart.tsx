import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from 'recharts';
import type { ThreatData } from '@/lib/threat-utils';

interface CompactRadarChartProps {
  data: ThreatData[];
}

const CompactRadarChart = ({ data }: CompactRadarChartProps) => {
  return (
    <div className="glass-card p-4 h-full">
      <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-2">
        Threat Radar
      </h3>

      <div className="h-36">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
            <PolarGrid 
              stroke="hsl(var(--border))" 
              strokeOpacity={0.5}
            />
            <PolarAngleAxis
              dataKey="name"
              tick={{ 
                fill: 'hsl(var(--muted-foreground))', 
                fontSize: 8, 
                fontFamily: 'JetBrains Mono' 
              }}
              tickLine={false}
            />
            <Radar
              name="Threat Level"
              dataKey="value"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary))"
              fillOpacity={0.15}
              strokeWidth={1.5}
              animationDuration={600}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CompactRadarChart;