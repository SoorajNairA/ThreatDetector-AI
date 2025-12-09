import { useState, useEffect, useMemo } from 'react';
import { toast } from 'sonner';
import { Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import Header from '@/components/dashboard/Header';
import SpeedometerGauge from '@/components/dashboard/SpeedometerGauge';
import ThreatPieChart from '@/components/dashboard/ThreatPieChart';
import CompactRadarChart from '@/components/dashboard/CompactRadarChart';
import CompactTrendGraph from '@/components/dashboard/CompactTrendGraph';
import LiveLineGraph from '@/components/dashboard/LiveLineGraph';
import ThreatBreakdown from '@/components/dashboard/ThreatBreakdown';
import AnalysisResults from '@/components/dashboard/AnalysisResults';
import ActivityLog from '@/components/dashboard/ActivityLog';
import ThreatHeatmap from '@/components/dashboard/ThreatHeatmap';
import ThreatTimeline from '@/components/dashboard/ThreatTimeline';
import { ApiKeySetupModal } from '@/components/ApiKeySetupModal';
import { useRealtimeThreats } from '@/hooks/useRealtimeThreats';
import { useApiKeySetup } from '@/hooks/useApiKeySetup';
import { useAnalysis } from '@/hooks/useAnalysis';
import { getCurrentTimeLabel, type ThreatData, type BreakdownItem, type Finding, type TrendPoint } from '@/lib/threat-utils';

const Index = () => {
  const { threats: realThreats, stats: realStats, isLoading, isConfigured, refresh } = useRealtimeThreats();
  const { hasApiKey, isChecking, isCreating, createDefaultApiKey } = useApiKeySetup();
  const { analyze, isAnalyzing, lastResult } = useAnalysis();
  const [showResults, setShowResults] = useState(false);
  const [trendData, setTrendData] = useState<TrendPoint[]>([]);
  const [testText, setTestText] = useState('');

  // FAKE DATA for testing layout
  const useFakeData = false;
  
  const fakeThreats = useMemo(() => {
    const now = new Date();
    const threats = [];
    
    // Generate 50 fake threats over the past 7 days
    for (let i = 0; i < 50; i++) {
      const daysAgo = Math.floor(Math.random() * 7);
      const hoursAgo = Math.floor(Math.random() * 24);
      const timestamp = new Date(now);
      timestamp.setDate(timestamp.getDate() - daysAgo);
      timestamp.setHours(timestamp.getHours() - hoursAgo);
      
      const riskScore = Math.random();
      threats.push({
        id: `fake-${i}`,
        timestamp: timestamp.toISOString(),
        risk_score: riskScore,
        risk_level: riskScore >= 0.8 ? 'HIGH' : riskScore >= 0.5 ? 'MEDIUM' : 'LOW',
        ai_generated: Math.random() > 0.6,
        intent: ['phishing', 'scam', 'spam', 'legitimate'][Math.floor(Math.random() * 4)],
        url_detected: Math.random() > 0.5,
        keywords: Math.random() > 0.5 ? ['urgent', 'verify', 'account', 'suspended'] : ['update', 'info'],
        content: 'Sample threat content for testing',
      });
    }
    
    return threats.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, []);

  const fakeStats = useMemo(() => {
    const high = fakeThreats.filter(t => t.risk_level === 'HIGH').length;
    const medium = fakeThreats.filter(t => t.risk_level === 'MEDIUM').length;
    const low = fakeThreats.filter(t => t.risk_level === 'LOW').length;
    
    return {
      total: fakeThreats.length,
      high,
      medium,
      low,
    };
  }, [fakeThreats]);

  const threats = useFakeData ? fakeThreats : realThreats;
  const stats = useFakeData ? fakeStats : realStats;

  // Calculate current threat level from latest threat
  const threatLevel = useMemo(() => {
    if (threats.length > 0) return threats[0].risk_score * 100;
    return 0;
  }, [threats]);

  // Calculate success rate from average model confidence
  // Fallback: use risk_score if confidence values don't exist
  const successRate = useMemo(() => {
    if (threats.length === 0) return 0;
    
    // Try using confidence scores
    const hasConfidence = threats.some(t => t.ai_confidence !== undefined || t.intent_confidence !== undefined);
    
    if (hasConfidence) {
      // Use confidence scores if available
      const totalConfidence = threats.reduce((sum, threat) => {
        const aiConf = threat.ai_confidence || 0;
        const intentConf = threat.intent_confidence || 0;
        return sum + ((aiConf + intentConf) / 2);
      }, 0);
      return (totalConfidence / threats.length) * 100;
    } else {
      // Fallback: estimate from risk scores
      // High risk = high confidence, Low risk = medium confidence
      const totalEstimated = threats.reduce((sum, threat) => {
        // Estimate confidence: risk_score with a baseline
        const estimated = (threat.risk_score * 0.8) + 0.2; // Scale 0.2-1.0
        return sum + estimated;
      }, 0);
      return (totalEstimated / threats.length) * 100;
    }
  }, [threats]);

  // Convert stats to chart data - by threat type
  const threatData = useMemo((): ThreatData[] => {
    if (threats.length === 0) return [];
    
    // Count threats by intent/type
    const typeCounts = threats.reduce((acc, threat) => {
      const type = threat.intent || 'unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Define colors for each threat type
    const typeColors: Record<string, string> = {
      phishing: 'hsl(0 72% 55%)',        // Red
      scam: 'hsl(262 50% 58%)',          // Purple
      spam: 'hsl(35 85% 55%)',           // Orange
      legitimate: 'hsl(152 55% 45%)',    // Green
      safe: 'hsl(152 55% 45%)',          // Green
      unknown: 'hsl(220 10% 55%)',       // Gray
    };

    return Object.entries(typeCounts).map(([type, count]) => ({
      name: type.charAt(0).toUpperCase() + type.slice(1),
      value: count,
      fill: typeColors[type] || 'hsl(var(--chart-1))',
    }));
  }, [threats]);

  // Convert stats to breakdown data - by threat type
  const breakdownData = useMemo((): BreakdownItem[] => {
    if (threats.length === 0) return [];
    
    // Count threats by intent/type
    const typeCounts = threats.reduce((acc, threat) => {
      const type = threat.intent || 'unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const total = threats.length;

    return Object.entries(typeCounts).map(([type, count]) => ({
      category: type.charAt(0).toUpperCase() + type.slice(1),
      count,
      percentage: (count / total) * 100,
    }));
  }, [threats]);

  // Convert latest threat OR lastResult to findings
  const findings = useMemo((): Finding[] => {
    // If we have a test analysis result, show that
    if (showResults && lastResult) {
      const analysis = lastResult.analysis;
      return [
        { label: 'Risk Level', value: lastResult.risk_level, severity: lastResult.risk_level === 'HIGH' ? 'critical' : lastResult.risk_level === 'MEDIUM' ? 'warning' : 'success' },
        { label: 'Risk Score', value: `${(lastResult.risk_score * 100).toFixed(1)}%`, severity: lastResult.risk_score >= 0.7 ? 'critical' : lastResult.risk_score >= 0.4 ? 'warning' : 'info' },
        { label: 'AI Generated', value: analysis.ai_generated ? 'Yes' : 'No', severity: analysis.ai_generated ? 'warning' : 'success' },
        { label: 'AI Confidence', value: `${(analysis.ai_confidence * 100).toFixed(1)}%`, severity: 'info' },
        { label: 'Intent', value: analysis.intent, severity: analysis.intent === 'phishing' || analysis.intent === 'scam' ? 'critical' : 'info' },
        { label: 'Intent Confidence', value: `${(analysis.intent_confidence * 100).toFixed(1)}%`, severity: 'info' },
        { label: 'URL Detected', value: analysis.url_detected ? 'Yes' : 'No', severity: analysis.url_detected ? 'warning' : 'success' },
        { label: 'Keywords Found', value: String(analysis.keywords?.length || 0), severity: (analysis.keywords?.length || 0) > 3 ? 'warning' : 'info' },
      ];
    }
    
    // Otherwise show latest threat from dashboard
    if (threats.length === 0) return [];
    const latestThreat = threats[0];
    return [
      { label: 'AI Generated', value: latestThreat.ai_generated ? 'Yes' : 'No', severity: latestThreat.ai_generated ? 'warning' : 'success' },
      { label: 'Intent', value: latestThreat.intent, severity: latestThreat.intent === 'phishing' || latestThreat.intent === 'scam' ? 'critical' : 'info' },
      { label: 'URL Detected', value: latestThreat.url_detected ? 'Yes' : 'No', severity: latestThreat.url_detected ? 'warning' : 'success' },
      { label: 'Keywords Found', value: String(latestThreat.keywords?.length || 0), severity: (latestThreat.keywords?.length || 0) > 3 ? 'warning' : 'info' },
    ];
  }, [threats, showResults, lastResult]);

  // Generate fake trend data
  useEffect(() => {
    if (useFakeData) {
      const now = new Date();
      const fakeTrend: TrendPoint[] = [];
      
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now);
        time.setMinutes(time.getMinutes() - i * 5);
        fakeTrend.push({
          label: getCurrentTimeLabel(time),
          value: 30 + Math.random() * 50,
          time: time.toISOString(),
        });
      }
      
      setTrendData(fakeTrend);
    }
  }, [useFakeData]);

  // Show connection status
  useEffect(() => {
    if (!isConfigured && !isLoading) {
      toast.info('Supabase not configured', {
        description: 'Real-time updates disabled. Configure VITE_SUPABASE_URL in .env',
      });
    }
  }, [isConfigured, isLoading]);

  const handleAnalyze = async () => {
    if (!testText.trim()) return;
    
    console.log('[Dashboard] Starting analysis...', { textLength: testText.length });
    
    try {
      const result = await analyze(testText, undefined, false); // Store in dashboard
      console.log('[Dashboard] Analysis result:', result);
      
      if (result) {
        setShowResults(true);
        toast.success('Analysis Complete', {
          description: `Risk Level: ${result.risk_level} (${(result.risk_score * 100).toFixed(1)}%)`,
        });
        setTimeout(() => refresh(), 500); // Refresh dashboard after analysis
      } else {
        console.error('[Dashboard] Analysis returned null');
        toast.error('Analysis Failed', {
          description: 'No result returned from analysis',
        });
      }
    } catch (error) {
      console.error('[Dashboard] Analysis error:', error);
      toast.error('Analysis Failed', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  return (
    <div className="min-h-screen bg-background grid-bg">
      <Header />

      {/* API Key Setup Modal */}
      <ApiKeySetupModal
        open={!isChecking && !hasApiKey}
        isCreating={isCreating}
        onCreateKey={createDefaultApiKey}
      />

      <main className="container px-4 py-5 space-y-4">
        {/* Top Row: Test Input (8 cols) + Threat Pie Chart (4 cols) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-8">
            <div className="glass-card p-6 border border-border/50 h-full">
              <h2 className="font-mono-display text-sm font-semibold text-foreground mb-4">
                Test Input
              </h2>
              <Textarea
                value={testText}
                onChange={(e) => setTestText(e.target.value)}
                placeholder="Enter text to analyze..."
                className="min-h-[240px] bg-secondary/30 border-border/50 focus:border-primary/50 font-mono text-sm mb-3"
              />
              <div className="flex items-center justify-between">
                <div className="text-xs text-muted-foreground">
                  {testText.length} chars
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setTestText('')}
                    disabled={!testText || isAnalyzing}
                  >
                    Clear
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleAnalyze}
                    disabled={!testText.trim() || isAnalyzing}
                    className="gap-2"
                  >
                    <Zap className="h-3 w-3" />
                    {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Threat Pie Chart - Right side */}
          <div className="lg:col-span-4">
            <ThreatPieChart data={threatData} />
          </div>
        </div>

        {/* Stat Cards Row - Below Test Input */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-card p-6 border border-border/50 hover:border-primary/50 transition-colors cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">Total Threats</span>
              <span className={`h-2 w-2 rounded-full ${isLoading ? 'bg-warning animate-pulse' : 'bg-success'}`} />
            </div>
            <div className="font-mono-display text-4xl font-bold text-foreground mb-1">{stats?.total || 0}</div>
            <div className="text-xs text-muted-foreground">Monitored in real-time</div>
          </div>
          
          <div className="glass-card p-6 border border-border/50 hover:border-destructive/50 transition-colors cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">High Risk</span>
              <span className="h-2 w-2 rounded-full bg-destructive animate-pulse" />
            </div>
            <div className="font-mono-display text-4xl font-bold text-destructive mb-1">{stats?.high || 0}</div>
            <div className="text-xs text-muted-foreground">Immediate attention required</div>
          </div>
          
          <div className="glass-card p-6 border border-border/50 hover:border-primary/50 transition-colors cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">Success Rate</span>
              <span className="h-2 w-2 rounded-full bg-warning" />
            </div>
            <div className="font-mono-display text-4xl font-bold text-foreground mb-1">
              {successRate.toFixed(0)}%
            </div>
            <div className="text-xs text-muted-foreground">Model prediction accuracy</div>
          </div>
        </div>

        {/* Main Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Live Line Graph */}
          <div className="lg:col-span-8">
            <LiveLineGraph baseValue={threatLevel} isLive={!isLoading} />
          </div>

          {/* Speedometer */}
          <div className="lg:col-span-4">
            <SpeedometerGauge value={threatLevel} isAnalyzing={false} />
          </div>
        </div>

        {/* Charts Row - Single component */}
        <div className="grid grid-cols-1 gap-4">
          <ThreatBreakdown data={breakdownData} />
        </div>

        {/* Heatmap + Timeline Row */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-8">
            <ThreatHeatmap threats={threats} />
          </div>
          <div className="lg:col-span-4">
            <ThreatTimeline threats={threats} />
          </div>
        </div>

        {/* Bottom Row - Analysis + Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-5">
            <AnalysisResults findings={findings} showResults={showResults} />
          </div>
          <div className="lg:col-span-7">
            <ActivityLog data={trendData} />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
