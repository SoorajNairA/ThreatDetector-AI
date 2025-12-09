import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { FileText, AlertCircle, CheckCircle, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import Header from '@/components/dashboard/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { guardianApi } from '@/services/api';

interface LogEntry {
  id: string;
  timestamp: string;
  text: string;
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
  risk_score: number;
  intent?: string;
  ai_generated?: boolean;
  ai_confidence?: number;
  intent_confidence?: number;
  style_score?: number;
  url_detected?: boolean;
  domains?: string[];
  keywords?: string[];
}

const Logs = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setIsLoading(true);
      const response = await guardianApi.getLogs();
      setLogs(response.logs || []);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      toast.error('Failed to load logs');
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'HIGH':
        return <AlertCircle className="h-5 w-5 text-destructive" />;
      case 'MEDIUM':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'LOW':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const getRiskBadgeVariant = (level: string): "destructive" | "default" | "secondary" => {
    switch (level) {
      case 'HIGH':
        return 'destructive';
      case 'MEDIUM':
        return 'default';
      case 'LOW':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const toggleExpanded = (logId: string) => {
    setExpandedLog(expandedLog === logId ? null : logId);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="text-muted-foreground">Loading logs...</div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Analysis Logs</h1>
          <p className="text-muted-foreground">
            View detailed history of all your threat analyses
          </p>
        </div>

        {logs.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground text-center">
                No logs yet. Start analyzing text to see your history here.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {logs.map((log) => {
              const isExpanded = expandedLog === log.id;
              
              return (
                <Card key={log.id} className="overflow-hidden">
                  <CardHeader className="cursor-pointer" onClick={() => toggleExpanded(log.id)}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        {getRiskIcon(log.risk_level)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <CardTitle className="text-lg">
                              {format(new Date(log.timestamp), 'PPpp')}
                            </CardTitle>
                            <Badge variant={getRiskBadgeVariant(log.risk_level)}>
                              {log.risk_level}
                            </Badge>
                          </div>
                          <CardDescription className="line-clamp-2">
                            {log.text}
                          </CardDescription>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </CardHeader>

                  {isExpanded && (
                    <CardContent className="pt-0 space-y-4">
                      {/* Full Text */}
                      <div>
                        <h4 className="font-semibold mb-2">Analyzed Text:</h4>
                        <div className="bg-muted p-4 rounded-lg">
                          <p className="text-sm whitespace-pre-wrap">{log.text}</p>
                        </div>
                      </div>

                      {/* Risk Score */}
                      <div>
                        <h4 className="font-semibold mb-2">Overall Risk Score:</h4>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-muted rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                log.risk_score >= 0.7
                                  ? 'bg-destructive'
                                  : log.risk_score >= 0.4
                                  ? 'bg-yellow-500'
                                  : 'bg-green-500'
                              }`}
                              style={{ width: `${log.risk_score * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-mono">
                            {(log.risk_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      {/* Classifier Results */}
                      <div>
                        <h4 className="font-semibold mb-3">Classifier Results:</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {/* AI Classifier */}
                          <div className="bg-muted p-3 rounded-lg">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium">AI Generated</span>
                              <Badge variant={log.ai_generated ? 'destructive' : 'secondary'}>
                                {log.ai_generated ? 'Yes' : 'No'}
                              </Badge>
                            </div>
                            {log.ai_confidence !== undefined && (
                              <p className="text-xs text-muted-foreground">
                                Confidence: {(log.ai_confidence * 100).toFixed(1)}%
                              </p>
                            )}
                          </div>

                          {/* Intent Classifier */}
                          <div className="bg-muted p-3 rounded-lg">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium">Intent</span>
                              <Badge>{log.intent || 'Unknown'}</Badge>
                            </div>
                            {log.intent_confidence !== undefined && (
                              <p className="text-xs text-muted-foreground">
                                Confidence: {(log.intent_confidence * 100).toFixed(1)}%
                              </p>
                            )}
                          </div>

                          {/* Stylometry Classifier */}
                          {log.style_score !== undefined && (
                            <div className="bg-muted p-3 rounded-lg">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium">Style Analysis</span>
                              </div>
                              <p className="text-xs text-muted-foreground">
                                Score: {(log.style_score * 100).toFixed(1)}%
                              </p>
                            </div>
                          )}

                          {/* URL Detection */}
                          <div className="bg-muted p-3 rounded-lg">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium">URL Detected</span>
                              <Badge variant={log.url_detected ? 'destructive' : 'secondary'}>
                                {log.url_detected ? 'Yes' : 'No'}
                              </Badge>
                            </div>
                            {log.domains && log.domains.length > 0 && (
                              <p className="text-xs text-muted-foreground">
                                Domains: {log.domains.join(', ')}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Keywords */}
                      {log.keywords && log.keywords.length > 0 && (
                        <div>
                          <h4 className="font-semibold mb-2">Detected Keywords:</h4>
                          <div className="flex flex-wrap gap-2">
                            {log.keywords.map((keyword, idx) => (
                              <Badge key={idx} variant="outline">
                                {keyword}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
};

export default Logs;
