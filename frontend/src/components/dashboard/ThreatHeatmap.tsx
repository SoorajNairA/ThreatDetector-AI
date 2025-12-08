import { useMemo } from 'react';
import { Activity } from 'lucide-react';

interface HeatmapData {
  day: string;
  hour: number;
  intensity: number;
}

interface ThreatHeatmapProps {
  threats?: Array<{
    timestamp: string;
    risk_score: number;
  }>;
}

const ThreatHeatmap = ({ threats = [] }: ThreatHeatmapProps) => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Process threats into heatmap data
  const heatmapData = useMemo(() => {
    const dataMap = new Map<string, { count: number; totalRisk: number }>();

    // Initialize all cells
    days.forEach((day, dayIndex) => {
      hours.forEach((hour) => {
        dataMap.set(`${dayIndex}-${hour}`, { count: 0, totalRisk: 0 });
      });
    });

    // Populate with actual threat data
    threats.forEach((threat) => {
      const date = new Date(threat.timestamp);
      const dayIndex = (date.getDay() + 6) % 7; // Convert Sunday=0 to Monday=0
      const hour = date.getHours();
      const key = `${dayIndex}-${hour}`;

      const current = dataMap.get(key) || { count: 0, totalRisk: 0 };
      dataMap.set(key, {
        count: current.count + 1,
        totalRisk: current.totalRisk + threat.risk_score,
      });
    });

    // Convert to array with intensity
    const data: HeatmapData[] = [];
    days.forEach((day, dayIndex) => {
      hours.forEach((hour) => {
        const key = `${dayIndex}-${hour}`;
        const cell = dataMap.get(key) || { count: 0, totalRisk: 0 };
        const intensity = cell.count > 0 ? cell.totalRisk / cell.count : 0;
        data.push({ day, hour, intensity });
      });
    });

    return data;
  }, [threats, days, hours]);

  const getIntensityColor = (intensity: number) => {
    if (intensity === 0) return 'bg-muted/30';
    if (intensity < 0.3) return 'bg-green-500/40 hover:bg-green-500/60';
    if (intensity < 0.5) return 'bg-yellow-500/50 hover:bg-yellow-500/70';
    if (intensity < 0.7) return 'bg-orange-500/60 hover:bg-orange-500/80';
    return 'bg-red-500/70 hover:bg-red-500/90';
  };

  const maxIntensity = Math.max(...heatmapData.map(d => d.intensity), 0.1);

  return (
    <div className="glass-card p-4 border border-border/50">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
            Threat Activity Heatmap
          </h3>
        </div>
        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
          <span>Low</span>
          <div className="flex gap-0.5">
            <div className="w-3 h-3 bg-green-500/60 border border-green-500 rounded-sm" />
            <div className="w-3 h-3 bg-yellow-500/70 border border-yellow-500 rounded-sm" />
            <div className="w-3 h-3 bg-orange-500/80 border border-orange-500 rounded-sm" />
            <div className="w-3 h-3 bg-red-500/90 border border-red-500 rounded-sm" />
          </div>
          <span>High</span>
        </div>
      </div>

      <div className="overflow-x-auto pb-2">
        <div className="inline-flex flex-col gap-1.5 min-w-full">
          {/* Hour labels */}
          <div className="flex gap-1 mb-2 pl-12">
            {[0, 4, 8, 12, 16, 20].map((hour) => (
              <div key={hour} className="w-6 text-center">
                <span className="font-mono-display text-[9px] text-muted-foreground">
                  {hour.toString().padStart(2, '0')}
                </span>
              </div>
            ))}
          </div>

          {/* Heatmap grid */}
          {days.map((day, dayIndex) => (
            <div key={day} className="flex gap-1 items-center">
              <span className="font-mono-display text-[10px] text-muted-foreground w-10 text-right pr-2">
                {day}
              </span>
              <div className="flex gap-1">
                {hours.map((hour) => {
                  const dataPoint = heatmapData.find(
                    (d) => d.day === day && d.hour === hour
                  );
                  const intensity = dataPoint?.intensity || 0;
                  
                  return (
                    <div
                      key={`${day}-${hour}`}
                      className={`w-3 h-5 rounded-sm transition-all cursor-pointer ${getIntensityColor(intensity)}`}
                      title={`${day} ${hour}:00 - Risk: ${(intensity * 100).toFixed(0)}%`}
                      style={{
                        opacity: intensity === 0 ? 0.4 : 0.8 + (intensity / maxIntensity) * 0.2
                      }}
                    />
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-3 text-[10px] text-muted-foreground text-center">
        {threats.length > 0 
          ? `Showing activity from ${threats.length} threat${threats.length !== 1 ? 's' : ''}`
          : 'No activity data available'}
      </div>
    </div>
  );
};

export default ThreatHeatmap;
