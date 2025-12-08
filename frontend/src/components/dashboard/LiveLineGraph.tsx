import { useEffect, useState, useRef } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface DataPoint {
  time: number;
  value: number;
}

interface LiveLineGraphProps {
  baseValue?: number;
  isLive?: boolean;
}

const LiveLineGraph = ({ baseValue = 50, isLive = true }: LiveLineGraphProps) => {
  const [data, setData] = useState<DataPoint[]>([]);
  const timeRef = useRef(0);

  useEffect(() => {
    // Initialize with some data
    const initialData: DataPoint[] = [];
    for (let i = 0; i < 30; i++) {
      initialData.push({
        time: i,
        value: baseValue + (Math.random() - 0.5) * 20,
      });
    }
    setData(initialData);
    timeRef.current = 30;
  }, [baseValue]);

  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setData((prev) => {
        const newPoint = {
          time: timeRef.current,
          value: baseValue + (Math.random() - 0.5) * 25 + Math.sin(timeRef.current * 0.1) * 10,
        };
        timeRef.current += 1;
        
        const updated = [...prev.slice(-29), newPoint];
        return updated;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [baseValue, isLive]);

  const minValue = Math.min(...data.map(d => d.value), 0);
  const maxValue = Math.max(...data.map(d => d.value), 100);

  return (
    <div className="glass-card p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
          Live Threat Feed
        </h3>
        <div className="flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
          </span>
          <span className="font-mono-display text-[10px] text-primary">STREAMING</span>
        </div>
      </div>
      
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="liveLineGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="hsl(var(--chart-1))" stopOpacity={0.3} />
                <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={1} />
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="time" 
              hide 
            />
            <YAxis 
              domain={[minValue - 10, maxValue + 10]}
              hide
            />
            <ReferenceLine 
              y={50} 
              stroke="hsl(var(--border))" 
              strokeDasharray="3 3" 
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="url(#liveLineGradient)"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="flex justify-between mt-2 px-1 flex-shrink-0">
        <span className="font-mono-display text-[9px] text-muted-foreground">30s ago</span>
        <span className="font-mono-display text-[9px] text-muted-foreground">now</span>
      </div>
    </div>
  );
};

export default LiveLineGraph;