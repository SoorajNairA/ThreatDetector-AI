import { Shield, Activity, Radio } from 'lucide-react';
import AccountDropdown from './AccountDropdown';

const Header = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/90 backdrop-blur-md">
      <div className="container flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-2.5">
          <div className="relative flex items-center justify-center w-8 h-8">
            <Shield className="h-6 w-6 text-primary" />
            <div className="absolute inset-0 bg-primary/10 blur-lg rounded-full" />
          </div>
          <div className="flex flex-col">
            <h1 className="font-mono-display text-base font-semibold tracking-tight text-foreground">
              Guardian
            </h1>
            <span className="text-[9px] uppercase tracking-widest text-muted-foreground font-mono-display -mt-0.5">
              Security Platform
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="status-pill-active hidden sm:flex">
            <Activity className="h-3 w-3" />
            <span>Active</span>
          </div>
          <div className="status-pill-live flex items-center pl-4">
            <Radio className="h-3 w-3 animate-pulse-subtle" />
            <span className="live-indicator ml-1">Live</span>
          </div>
          <AccountDropdown />
        </div>
      </div>
    </header>
  );
};

export default Header;