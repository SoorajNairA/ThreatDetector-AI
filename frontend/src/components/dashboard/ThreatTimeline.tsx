import { useMemo } from 'react';
import { Clock, AlertTriangle, ShieldAlert, Info } from 'lucide-react';

interface Threat {
  id: string;
  timestamp: string;
  risk_score: number;
  risk_level: string;
  intent: string;
  content?: string;
}

interface ThreatTimelineProps {
  threats?: Threat[];
}

const ThreatTimeline = ({ threats = [] }: ThreatTimelineProps) => {
  const recentThreats = useMemo(() => {
    return threats.slice(0, 2); // Show last 2 threats
  }, [threats]);

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = Math.floor((now.getTime() - then.getTime()) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'HIGH':
        return <ShieldAlert className="h-3.5 w-3.5 text-destructive" />;
      case 'MEDIUM':
        return <AlertTriangle className="h-3.5 w-3.5 text-warning" />;
      default:
        return <Info className="h-3.5 w-3.5 text-success" />;
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'HIGH':
        return 'border-destructive/50 bg-destructive/5';
      case 'MEDIUM':
        return 'border-warning/50 bg-warning/5';
      default:
        return 'border-success/50 bg-success/5';
    }
  };

  return (
    <div className="glass-card p-4 border border-border/50 flex flex-col" style={{ height: '314px' }}>
      <div className="flex items-center gap-2 mb-4 flex-shrink-0">
        <Clock className="h-4 w-4 text-primary" />
        <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
          Recent Threats
        </h3>
        <span className="ml-auto font-mono-display text-[10px] text-muted-foreground">
          Last 2
        </span>
      </div>

      <div className="flex-1 space-y-3 pr-1 min-h-0 flex flex-col justify-center">
        {recentThreats.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <Clock className="h-8 w-8 mb-2 opacity-30" />
            <p className="text-xs">No recent threats</p>
          </div>
        ) : (
          recentThreats.map((threat, index) => (
            <div
              key={threat.id}
              className={`p-3 rounded-md border transition-all hover:scale-[1.02] cursor-pointer ${getRiskColor(threat.risk_level)}`}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {getRiskIcon(threat.risk_level)}
                  <span className="font-mono-display text-[11px] uppercase tracking-wide text-foreground/90 whitespace-nowrap">
                    {threat.risk_level}
                  </span>
                </div>
                <span className="font-mono-display text-[10px] text-muted-foreground whitespace-nowrap">
                  {getTimeAgo(threat.timestamp)}
                </span>
              </div>
              
              <div className="flex items-center justify-between gap-3">
                <div className="flex flex-col gap-0.5 min-w-0 flex-1">
                  <span className="text-[10px] text-muted-foreground">Intent:</span>
                  <span className="font-mono-display text-[11px] text-foreground capitalize truncate">
                    {threat.intent}
                  </span>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className="text-[10px] text-muted-foreground whitespace-nowrap">Risk Score</span>
                  <div className="font-mono-display text-sm font-semibold text-foreground">
                    {(threat.risk_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {recentThreats.length > 0 && (
        <div className="mt-3 pt-3 border-t border-border/30 flex-shrink-0">
          <div className="flex justify-between text-[9px] text-muted-foreground">
            <span>Showing {recentThreats.length} of {threats.length} threats</span>
            <span className="text-primary">Live monitoring active</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ThreatTimeline;
