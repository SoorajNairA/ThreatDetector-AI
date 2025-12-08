import { Shield, AlertTriangle, XOctagon, CheckCircle } from 'lucide-react';
import type { BreakdownItem } from '@/lib/threat-utils';

interface ThreatBreakdownProps {
  data: BreakdownItem[];
}

const getThreatTypeIcon = (category: string) => {
  const lowerCategory = category.toLowerCase();
  switch (lowerCategory) {
    case 'phishing':
      return <XOctagon className="h-3.5 w-3.5 text-destructive" />;
    case 'scam':
      return <AlertTriangle className="h-3.5 w-3.5 text-warning" />;
    case 'spam':
      return <Shield className="h-3.5 w-3.5 text-chart-3" />;
    case 'legitimate':
      return <CheckCircle className="h-3.5 w-3.5 text-success" />;
    default:
      return <Shield className="h-3.5 w-3.5 text-muted-foreground" />;
  }
};

const getThreatTypeBg = (category: string) => {
  const lowerCategory = category.toLowerCase();
  switch (lowerCategory) {
    case 'phishing':
      return 'bg-destructive/8 border-destructive/20';
    case 'scam':
      return 'bg-warning/8 border-warning/20';
    case 'spam':
      return 'bg-chart-3/8 border-chart-3/20';
    case 'legitimate':
      return 'bg-success/8 border-success/20';
    default:
      return 'bg-muted/8 border-muted/20';
  }
};

const ThreatBreakdown = ({ data }: ThreatBreakdownProps) => {
  return (
    <div className="glass-card p-4 h-full">
      <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-3">
        Type Breakdown
      </h3>
      
      <div className="space-y-2.5">
        {data.map((item, index) => (
          <div
            key={index}
            className={`p-3 rounded-md border transition-all duration-200 hover:translate-x-0.5 ${getThreatTypeBg(item.category)}`}
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <div className="flex items-center gap-2">
                {getThreatTypeIcon(item.category)}
                <span className="font-mono-display text-xs font-medium text-foreground">
                  {item.category}
                </span>
              </div>
              <span className="font-mono-display text-xs font-semibold text-foreground">
                {item.count}
              </span>
            </div>
            <div className="ml-5.5">
              <div className="w-full bg-border/30 rounded-full h-1.5 overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-500"
                  style={{ width: `${item.percentage}%` }}
                />
              </div>
              <span className="text-[10px] text-muted-foreground mt-0.5 inline-block">
                {item.percentage.toFixed(1)}% of total
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ThreatBreakdown;