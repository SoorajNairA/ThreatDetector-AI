import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { ThreatData } from '@/lib/threat-utils';

interface ThreatPieChartProps {
  data: ThreatData[];
}

const COLORS = [
  'hsl(var(--chart-1))',
  'hsl(var(--chart-2))',
  'hsl(var(--chart-3))',
  'hsl(var(--chart-4))',
  'hsl(var(--chart-5))',
  'hsl(var(--chart-6))',
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card px-3 py-2 border-border/50">
        <p className="font-mono-display text-xs text-foreground">
          {payload[0].name}: <span className="text-primary font-semibold">{payload[0].value}%</span>
        </p>
      </div>
    );
  }
  return null;
};

const CustomLegend = ({ payload }: any) => {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-2 justify-center mt-4">
      {payload?.map((entry: any, index: number) => (
        <div key={entry.value} className="flex items-center gap-1.5">
          <div
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: COLORS[index % COLORS.length] }}
          />
          <span className="font-mono-display text-xs text-muted-foreground">
            {entry.value}
          </span>
        </div>
      ))}
    </div>
  );
};

const ThreatPieChart = ({ data }: ThreatPieChartProps) => {
  const filteredData = data.filter((item) => item.value > 0);

  return (
    <div className="glass-card p-5 h-full flex flex-col">
      <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-3">
        Threat Types
      </h3>
      
      <div className="flex-1 min-h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={filteredData}
              cx="50%"
              cy="45%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
              animationBegin={0}
              animationDuration={600}
            >
              {filteredData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.fill || COLORS[index % COLORS.length]}
                  stroke="hsl(var(--background))"
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend content={<CustomLegend />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ThreatPieChart;
