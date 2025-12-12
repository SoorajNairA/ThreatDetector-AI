/**
 * Landing page for unauthenticated users
 */
import { Link } from 'react-router-dom';
import { Shield, Lock, Zap, BarChart3, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Landing = () => {
  return (
    <div className="min-h-screen bg-background grid-bg">
      {/* Header */}
      <header className="border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="container px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            <span className="font-mono-display text-lg font-bold text-foreground">Guardian</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login">
              <Button variant="ghost" className="font-mono-display">
                Sign In
              </Button>
            </Link>
            <Link to="/register">
              <Button className="font-mono-display">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container px-4">
        <div className="max-w-6xl mx-auto">
          {/* Hero */}
          <div className="py-20 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6">
              <Lock className="h-4 w-4 text-primary" />
              <span className="font-mono-display text-xs text-primary uppercase tracking-wider">
                AI-Powered Threat Detection
              </span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-6 font-mono-display">
              Protect Your Digital
              <br />
              <span className="text-primary">Assets with AI</span>
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Real-time threat detection, analysis, and monitoring powered by advanced machine learning.
              Keep your systems secure with Guardian Security Platform.
            </p>

            <div className="flex items-center justify-center gap-4">
              <Link to="/register">
                <Button size="lg" className="font-mono-display text-base">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline" className="font-mono-display text-base">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 py-20">
            <div className="glass-card p-6 border border-border/50">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-mono-display text-lg font-semibold text-foreground mb-2">
                Real-Time Analysis
              </h3>
              <p className="text-sm text-muted-foreground">
                Instant threat detection with AI-powered classifiers analyzing text, URLs, and behavioral patterns.
              </p>
            </div>

            <div className="glass-card p-6 border border-border/50">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-mono-display text-lg font-semibold text-foreground mb-2">
                Advanced Analytics
              </h3>
              <p className="text-sm text-muted-foreground">
                Comprehensive dashboards with risk scoring, threat categorization, and trend analysis.
              </p>
            </div>

            <div className="glass-card p-6 border border-border/50">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-mono-display text-lg font-semibold text-foreground mb-2">
                Secure API Access
              </h3>
              <p className="text-sm text-muted-foreground">
                Generate and manage API keys with per-user authentication and usage tracking.
              </p>
            </div>
          </div>

          {/* CTA Section */}
          <div className="py-20 text-center">
            <div className="glass-card p-12 border border-border/50">
              <h2 className="text-3xl font-bold text-foreground mb-4 font-mono-display">
                Ready to Secure Your Platform?
              </h2>
              <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
                Join thousands of developers protecting their applications with Guardian Security Platform.
              </p>
              <Link to="/register">
                <Button size="lg" className="font-mono-display text-base">
                  Create Your Account
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8">
        <div className="container px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <span className="font-mono-display text-sm text-muted-foreground">
                © 2025 Guardian Security Platform
              </span>
            </div>
            <div className="flex items-center gap-6">
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Documentation
              </a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                API
              </a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Support
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
