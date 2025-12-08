import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, ArrowLeft, Beaker, Zap, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useAnalysis } from '@/hooks/useAnalysis';

const Sandbox = () => {
  const [testText, setTestText] = useState('');
  const { analyze, isAnalyzing, lastResult } = useAnalysis();

  const sampleTexts = [
    {
      name: 'Phishing Example',
      text: 'URGENT! Your account has been compromised. Click here immediately to verify your identity: http://bit.ly/secure-verify',
      risk: 'HIGH'
    },
    {
      name: 'Scam Example',
      text: 'Congratulations! You won $1,000,000! Send your bank account number and social security number to claim your prize now!',
      risk: 'HIGH'
    },
    {
      name: 'Suspicious Message',
      text: 'FINAL NOTICE: Your payment is overdue. Click here within 24 hours to avoid legal action.',
      risk: 'MEDIUM'
    },
    {
      name: 'Normal Message',
      text: 'Hey, just checking in to see how you are doing. Let me know if you want to grab coffee this weekend!',
      risk: 'LOW'
    }
  ];

  const handleAnalyze = async () => {
    if (!testText.trim()) return;
    await analyze(testText, undefined, true); // Pass sandbox=true
  };

  const loadSample = (text: string) => {
    setTestText(text);
  };

  const getRiskColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'HIGH': return 'text-red-500 bg-red-500/10 border-red-500/30';
      case 'MEDIUM': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      case 'LOW': return 'text-green-500 bg-green-500/10 border-green-500/30';
      default: return 'text-muted-foreground bg-muted/10 border-border/30';
    }
  };

  return (
    <div className="min-h-screen bg-background grid-bg">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="container px-4 py-4 flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-mono-display text-lg font-bold text-foreground">Guardian</span>
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="font-mono-display text-sm text-foreground">Sandbox</span>
        </div>
      </header>

      <div className="container px-4 py-6">
        <div className="flex gap-6">
          {/* Sidebar Navigation */}
          <aside className="w-56 shrink-0">
            <nav className="glass-card p-3 border border-border/50">
              <div className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground px-3 py-2">
                Developer Tools
              </div>
              <button
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md bg-primary/10 text-primary font-mono-display text-sm"
              >
                <Beaker className="h-4 w-4" />
                Sandbox
              </button>
            </nav>

            <Link
              to="/settings"
              className="flex items-center gap-2 mt-4 px-3 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Settings
            </Link>
          </aside>

          {/* Main Content */}
          <main className="flex-1 max-w-5xl">
            {/* Info Banner */}
            <div className="glass-card p-4 border border-primary/30 bg-primary/5 mb-6">
              <div className="flex items-start gap-3">
                <Beaker className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                <div>
                  <h2 className="font-mono-display text-sm font-semibold text-foreground mb-1">
                    Development Sandbox
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Test the threat analysis API in a safe environment. Results are not stored in your dashboard.
                    Use sample texts or write your own to see how the classifier ensemble works.
                  </p>
                </div>
              </div>
            </div>

            {/* Sample Texts */}
            <div className="glass-card p-6 border border-border/50 mb-6">
              <h2 className="font-mono-display text-sm font-semibold text-foreground mb-4">
                Sample Texts
              </h2>
              <div className="grid grid-cols-2 gap-3">
                {sampleTexts.map((sample) => (
                  <button
                    key={sample.name}
                    onClick={() => loadSample(sample.text)}
                    className="text-left p-3 rounded-md bg-secondary/30 border border-border/50 hover:border-primary/50 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono-display text-xs font-semibold text-foreground">
                        {sample.name}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded font-mono-display ${getRiskColor(sample.risk)} border`}>
                        {sample.risk}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {sample.text}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Input Area */}
            <div className="glass-card p-6 border border-border/50 mb-6">
              <h2 className="font-mono-display text-sm font-semibold text-foreground mb-4">
                Test Input
              </h2>
              <Textarea
                value={testText}
                onChange={(e) => setTestText(e.target.value)}
                placeholder="Enter text to analyze... Try pasting a suspicious email, social media post, or any text you want to test."
                className="min-h-[150px] bg-secondary/30 border-border/50 focus:border-primary/50 font-mono text-sm mb-4"
              />
              <div className="flex items-center justify-between">
                <div className="text-xs text-muted-foreground">
                  {testText.length} characters
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setTestText('')}
                    disabled={!testText || isAnalyzing}
                  >
                    Clear
                  </Button>
                  <Button
                    onClick={handleAnalyze}
                    disabled={!testText.trim() || isAnalyzing}
                    className="gap-2"
                  >
                    <Zap className="h-4 w-4" />
                    {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                  </Button>
                </div>
              </div>
            </div>

            {/* Results */}
            {lastResult && (
              <div className="glass-card p-6 border border-border/50">
                <h2 className="font-mono-display text-sm font-semibold text-foreground mb-4">
                  Analysis Results
                </h2>

                {/* Risk Level */}
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-2">
                    <div className={`px-4 py-2 rounded-md border ${getRiskColor(lastResult.risk_level)} font-mono-display text-lg font-bold`}>
                      {lastResult.risk_level}
                    </div>
                    <div className="text-2xl font-mono-display font-bold text-foreground">
                      {(lastResult.risk_score * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Risk Score</div>
                  </div>
                </div>

                {/* Classifier Breakdown */}
                <div className="space-y-4">
                  <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
                    Classifier Breakdown
                  </h3>

                  {/* AI Classifier */}
                  <div className="p-3 rounded-md bg-secondary/20 border border-border/30">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono-display text-sm font-semibold text-foreground">
                        AI Detection
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${lastResult.analysis.ai_generated ? 'bg-yellow-500/10 text-yellow-500' : 'bg-green-500/10 text-green-500'}`}>
                        {lastResult.analysis.ai_generated ? 'AI Generated' : 'Human Written'}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Confidence: {(lastResult.analysis.ai_confidence * 100).toFixed(1)}%
                    </div>
                  </div>

                  {/* Intent Classifier */}
                  <div className="p-3 rounded-md bg-secondary/20 border border-border/30">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono-display text-sm font-semibold text-foreground">
                        Intent Analysis
                      </span>
                      <span className="text-xs px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30">
                        {lastResult.analysis.intent}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Confidence: {(lastResult.analysis.intent_confidence * 100).toFixed(1)}%
                    </div>
                  </div>

                  {/* Stylometry */}
                  <div className="p-3 rounded-md bg-secondary/20 border border-border/30">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono-display text-sm font-semibold text-foreground">
                        Writing Style
                      </span>
                      <span className="text-xs text-muted-foreground">
                        Human-likeness: {(lastResult.analysis.style_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  {/* URL Detection */}
                  {lastResult.analysis.url_detected && (
                    <div className="p-3 rounded-md bg-secondary/20 border border-border/30">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono-display text-sm font-semibold text-foreground">
                          URL Detection
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded bg-red-500/10 text-red-500">
                          {lastResult.analysis.domains?.length || 0} URL(s)
                        </span>
                      </div>
                      {lastResult.analysis.domains && lastResult.analysis.domains.length > 0 && (
                        <div className="text-xs text-muted-foreground">
                          Domains: {lastResult.analysis.domains.join(', ')}
                        </div>
                      )}
                      <div className="text-xs text-muted-foreground mt-1">
                        Risk Score: {(lastResult.analysis.url_score * 100).toFixed(1)}%
                      </div>
                    </div>
                  )}

                  {/* Keywords */}
                  {lastResult.analysis.keywords && lastResult.analysis.keywords.length > 0 && (
                    <div className="p-3 rounded-md bg-secondary/20 border border-border/30">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono-display text-sm font-semibold text-foreground">
                          Risk Keywords
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded bg-orange-500/10 text-orange-500">
                          {lastResult.analysis.keywords.length} found
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {lastResult.analysis.keywords.slice(0, 10).map((keyword, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-0.5 rounded bg-muted/50 text-muted-foreground border border-border/30"
                          >
                            {keyword}
                          </span>
                        ))}
                        {lastResult.analysis.keywords.length > 10 && (
                          <span className="text-xs text-muted-foreground">
                            +{lastResult.analysis.keywords.length - 10} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Info Note */}
                <div className="mt-6 p-3 rounded-md bg-muted/20 border border-border/30 flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                  <p className="text-xs text-muted-foreground">
                    <strong>Note:</strong> Sandbox results are for testing only and are not stored in your dashboard or threat history.
                  </p>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default Sandbox;
