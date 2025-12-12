import { User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

const AccountDropdown = () => {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const handleSignOut = async () => {
    await signOut();
    navigate('/landing');
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="glass-card border-border/50 bg-glass-bg/60 hover:border-primary/50 hover:bg-glass-bg/80 transition-all duration-300 gap-2"
        >
          <User className="h-4 w-4" />
          <span className="hidden sm:inline font-mono-display text-xs">ACCOUNT</span>
          <ChevronDown className="h-3 w-3" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="w-48 glass-card border-border/50 bg-popover/95 backdrop-blur-xl"
      >
        {user && (
          <>
            <DropdownMenuLabel className="font-mono-display text-xs">
              {user.email}
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-border/50" />
          </>
        )}
        <DropdownMenuItem
          onClick={() => navigate('/settings')}
          className="gap-2 cursor-pointer hover:bg-primary/10 focus:bg-primary/10"
        >
          <Settings className="h-4 w-4" />
          <span>Settings</span>
        </DropdownMenuItem>
        {user && (
          <>
            <DropdownMenuSeparator className="bg-border/50" />
            <DropdownMenuItem
              onClick={handleSignOut}
              className="gap-2 cursor-pointer hover:bg-destructive/10 focus:bg-destructive/10 text-destructive"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out</span>
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default AccountDropdown;
