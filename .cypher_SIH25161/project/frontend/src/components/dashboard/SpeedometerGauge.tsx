import { useEffect, useState, useRef } from 'react';
import { getSeverityLabel } from '@/lib/threat-utils';

interface SpeedometerGaugeProps {
  value: number;
  isAnalyzing: boolean;
}

const SpeedometerGauge = ({ value, isAnalyzing }: SpeedometerGaugeProps) => {
  const [displayValue, setDisplayValue] = useState(0);
  const animationRef = useRef<number>();
  const intervalRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (isAnalyzing) {
      intervalRef.current = setInterval(() => {
        setDisplayValue(Math.floor(Math.random() * 100));
      }, 200);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      const startValue = displayValue;
      const endValue = value;
      const duration = 800;
      const startTime = Date.now();

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentValue = startValue + (endValue - startValue) * easeOut;
        setDisplayValue(Math.round(currentValue));

        if (progress < 1) {
          animationRef.current = requestAnimationFrame(animate);
        }
      };

      animationRef.current = requestAnimationFrame(animate);
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [value, isAnalyzing]);

  const getColor = () => {
    if (displayValue <= 25) return 'hsl(var(--success))';
    if (displayValue <= 50) return 'hsl(var(--chart-1))';
    if (displayValue <= 75) return 'hsl(var(--warning))';
    return 'hsl(var(--danger))';
  };

  const getColorClass = () => {
    if (displayValue <= 25) return 'text-success';
    if (displayValue <= 50) return 'text-chart-1';
    if (displayValue <= 75) return 'text-warning';
    return 'text-danger';
  };

  const needleRotation = -90 + (displayValue / 100) * 180;
  const color = getColor();

  return (
    <div className="glass-card p-4 flex flex-col items-center justify-center h-full">
      <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-3">
        Threat Level
      </h3>
      
      <div className="relative w-36 h-20">
        <svg viewBox="0 0 200 110" className="w-full h-full">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="hsl(var(--success))" />
              <stop offset="33%" stopColor="hsl(var(--chart-1))" />
              <stop offset="66%" stopColor="hsl(var(--warning))" />
              <stop offset="100%" stopColor="hsl(var(--danger))" />
            </linearGradient>
          </defs>

          {/* Background arc */}
          <path
            d="M 25 100 A 75 75 0 0 1 175 100"
            fill="none"
            stroke="hsl(var(--secondary))"
            strokeWidth="8"
            strokeLinecap="round"
          />

          {/* Gradient arc */}
          <path
            d="M 25 100 A 75 75 0 0 1 175 100"
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(displayValue / 100) * 235.6} 235.6`}
            className="transition-all duration-150"
          />

          {/* Needle */}
          <g transform={`rotate(${needleRotation}, 100, 100)`}>
            <polygon
              points="100,40 96,100 104,100"
              fill={color}
              className="transition-all duration-150"
            />
          </g>

          {/* Center circle */}
          <circle
            cx="100"
            cy="100"
            r="8"
            fill="hsl(var(--background))"
            stroke={color}
            strokeWidth="2"
            className="transition-all duration-150"
          />
        </svg>
      </div>

      <div className="mt-2 text-center">
        <div className={`font-mono-display text-2xl font-bold ${getColorClass()} transition-colors duration-150`}>
          {displayValue}%
        </div>
        <div className={`font-mono-display text-[10px] uppercase tracking-wider ${getColorClass()} opacity-80`}>
          {getSeverityLabel(displayValue)}
        </div>
      </div>

      {isAnalyzing && (
        <div className="mt-2 flex items-center gap-1.5 text-primary">
          <div className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          <span className="font-mono-display text-[10px] uppercase">Scanning...</span>
        </div>
      )}
    </div>
  );
};

export default SpeedometerGauge;