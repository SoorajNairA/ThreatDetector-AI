import { useState, useEffect, useMemo } from 'react';
import { toast } from 'sonner';
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
import { getCurrentTimeLabel, type ThreatData, type BreakdownItem, type Finding, type TrendPoint } from '@/lib/threat-utils';

const Index = () => {
  const { threats: realThreats, stats: realStats, isLoading, isConfigured, refresh } = useRealtimeThreats();
  const { hasApiKey, isChecking, isCreating, createDefaultApiKey } = useApiKeySetup();
  const [showResults, setShowResults] = useState(false);
  const [trendData, setTrendData] = useState<TrendPoint[]>([]);

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

  // Calculate current risk score from latest threat
  const riskScore = useMemo(() => {
    if (threats.length > 0) return threats[0].risk_score * 100;
    return 0;
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
      phishing: 'hsl(var(--destructive))',
      scam: 'hsl(var(--warning))',
      spam: 'hsl(var(--chart-3))',
      legitimate: 'hsl(var(--success))',
      unknown: 'hsl(var(--muted))',
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

  // Convert latest threat to findings
  const findings = useMemo((): Finding[] => {
    if (threats.length === 0) return [];
    const latestThreat = threats[0];
    return [
      { label: 'AI Generated', value: latestThreat.ai_generated ? 'Yes' : 'No', severity: latestThreat.ai_generated ? 'warning' : 'success' },
      { label: 'Intent', value: latestThreat.intent, severity: latestThreat.intent === 'phishing' || latestThreat.intent === 'scam' ? 'critical' : 'info' },
      { label: 'URL Detected', value: latestThreat.url_detected ? 'Yes' : 'No', severity: latestThreat.url_detected ? 'warning' : 'success' },
      { label: 'Keywords Found', value: String(latestThreat.keywords?.length || 0), severity: (latestThreat.keywords?.length || 0) > 3 ? 'warning' : 'info' },
    ];
  }, [threats]);

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
        {/* Hero Section - Key Metrics */}
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
              <span className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">Current Risk</span>
              <span className="h-2 w-2 rounded-full bg-warning" />
            </div>
            <div className="font-mono-display text-4xl font-bold text-foreground mb-1">
              {riskScore.toFixed(0)}%
            </div>
            <div className="text-xs text-muted-foreground">Real-time risk level</div>
          </div>
        </div>

        {/* Main Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Live Line Graph */}
          <div className="lg:col-span-8">
            <LiveLineGraph baseValue={riskScore} isLive={!isLoading} />
          </div>

          {/* Speedometer */}
          <div className="lg:col-span-4">
            <SpeedometerGauge value={riskScore} isAnalyzing={false} />
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          <CompactRadarChart data={threatData} />
          <CompactTrendGraph data={trendData} />
          <ThreatPieChart data={threatData} />
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
