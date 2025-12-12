import { CheckCircle, AlertTriangle, XOctagon, Info, Clock } from 'lucide-react';
import type { Finding } from '@/lib/threat-utils';

interface AnalysisResultsProps {
  findings: Finding[];
  showResults: boolean;
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'safe':
      return <CheckCircle className="h-4 w-4 text-success" />;
    case 'warning':
      return <AlertTriangle className="h-4 w-4 text-warning" />;
    case 'danger':
      return <XOctagon className="h-4 w-4 text-danger" />;
    default:
      return <Info className="h-4 w-4 text-info" />;
  }
};

const getTypeBg = (type: string) => {
  switch (type) {
    case 'safe':
      return 'border-success/20 bg-success/5';
    case 'warning':
      return 'border-warning/20 bg-warning/5';
    case 'danger':
      return 'border-danger/20 bg-danger/5';
    default:
      return 'border-info/20 bg-info/5';
  }
};

const AnalysisResults = ({ findings, showResults }: AnalysisResultsProps) => {
  if (!showResults || findings.length === 0) {
    return (
      <div className="glass-card p-4 h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-muted/30 flex items-center justify-center">
            <Info className="h-6 w-6 text-muted-foreground" />
          </div>
          <p className="font-mono-display text-xs text-muted-foreground">
            Awaiting analysis data
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-4 h-full">
      <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-3">
        Findings
      </h3>
      
      <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
        {findings.map((finding, index) => (
          <div
            key={finding.id}
            className={`p-2.5 rounded-md border transition-all duration-200 animate-fade-in ${getTypeBg(finding.type)}`}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-start gap-2">
              {getTypeIcon(finding.type)}
              <div className="flex-1 min-w-0">
                <h4 className="font-mono-display text-xs font-medium text-foreground truncate">
                  {finding.title}
                </h4>
                <p className="mt-0.5 text-[10px] text-muted-foreground line-clamp-2">
                  {finding.description}
                </p>
                <div className="mt-1.5 flex items-center gap-1 text-muted-foreground">
                  <Clock className="h-2.5 w-2.5" />
                  <span className="font-mono-display text-[9px]">{finding.timestamp}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AnalysisResults;