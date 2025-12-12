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
  threats?: Array<{ timestamp: string; risk_score: number; id?: string }>;
}

const LiveLineGraph = ({ baseValue = 50, isLive = true, threats = [] }: LiveLineGraphProps) => {
  const [data, setData] = useState<DataPoint[]>([]);
  const [currentValue, setCurrentValue] = useState(0);
  const [targetValue, setTargetValue] = useState(0);
  const timeRef = useRef(0);
  const lastThreatIdRef = useRef<string | null>(null);
  const lastUpdateTimeRef = useRef<number>(Date.now());

  useEffect(() => {
    const initialData: DataPoint[] = [];
    const recentThreats = threats.slice(0, 30).reverse();
    
    for (let i = 0; i < 30; i++) {
      if (i < recentThreats.length) {
        initialData.push({
          time: i,
          value: recentThreats[i].risk_score * 100,
        });
      } else {
        initialData.push({
          time: i,
          value: 0,
        });
      }
    }
    setData(initialData);
    const initialValue = recentThreats.length > 0 ? recentThreats[recentThreats.length - 1].risk_score * 100 : 0;
    setCurrentValue(initialValue);
    setTargetValue(initialValue);
    timeRef.current = 30;
    
    if (threats.length > 0) {
      lastThreatIdRef.current = threats[0].id || threats[0].timestamp;
      lastUpdateTimeRef.current = Date.now();
    }
  }, []);

  useEffect(() => {
    if (threats.length === 0) return;

    const latestThreat = threats[0];
    const latestId = latestThreat.id || latestThreat.timestamp;

    if (latestId !== lastThreatIdRef.current) {
      const newValue = latestThreat.risk_score * 100;
      setTargetValue(newValue);
      lastThreatIdRef.current = latestId;
      lastUpdateTimeRef.current = Date.now();
    }
  }, [threats]);

  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setData((prev) => {
        const timeSinceUpdate = (Date.now() - lastUpdateTimeRef.current) / 1000;
        
        const decayRate = 0.05;
        const decayedTarget = targetValue * Math.exp(-decayRate * timeSinceUpdate);
        
        setCurrentValue(prev => {
          const diff = decayedTarget - prev;
          return prev + diff * 0.3;
        });
        
        setTargetValue(decayedTarget);
        
        const newPoint = {
          time: timeRef.current,
          value: currentValue + (Math.random() - 0.5) * 3,
        };
        timeRef.current += 1;
        
        return [...prev.slice(-29), newPoint];
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isLive, currentValue, targetValue]);

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