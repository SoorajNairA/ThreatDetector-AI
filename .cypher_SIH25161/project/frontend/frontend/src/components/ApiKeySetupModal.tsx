/**
 * API Key Setup Modal - prompts users to create their first API key
 */
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Key, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ApiKeySetupModalProps {
  open: boolean;
  isCreating: boolean;
  onCreateKey: () => void;
}

export const ApiKeySetupModal = ({ open, isCreating, onCreateKey }: ApiKeySetupModalProps) => {
  const navigate = useNavigate();

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center justify-center mb-4">
            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Key className="h-6 w-6 text-primary" />
            </div>
          </div>
          <DialogTitle className="text-center font-mono-display">API Key Required</DialogTitle>
          <DialogDescription className="text-center">
            You need an API key to use the Guardian Security Platform. This key will be used to authenticate your requests to the backend.
          </DialogDescription>
        </DialogHeader>
        
        <div className="bg-secondary/20 border border-border/30 rounded-md p-4 my-4">
          <p className="text-sm text-muted-foreground">
            Click "Create API Key" to generate your first key automatically, or go to Settings to manage your keys manually.
          </p>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            onClick={() => navigate('/settings')}
            className="w-full sm:w-auto"
            disabled={isCreating}
          >
            Go to Settings
          </Button>
          <Button
            onClick={onCreateKey}
            disabled={isCreating}
            className="w-full sm:w-auto gap-2"
          >
            {isCreating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Key className="h-4 w-4" />
                Create API Key
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
