import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Key, ArrowLeft, Copy, Check, LogOut, CheckCircle2, Beaker, Lock } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';
import { getApiKey, setApiKey as saveApiKey, listAPIKeys, createAPIKey, deleteAPIKey, type APIKeyResponse } from '@/services/api';

interface PrivacySettings {
  allow_training_data: boolean;
  training_consent_at: string | null;
}

const Settings = () => {
  const [apiKey, setApiKey] = useState('');
  const [apiKeys, setApiKeys] = useState<APIKeyResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [copied, setCopied] = useState(false);
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null);
  const [showInactive, setShowInactive] = useState(false);
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings | null>(null);
  const [isUpdatingPrivacy, setIsUpdatingPrivacy] = useState(false);
  const { user, signOut } = useAuth();

  // Load current API key and list on mount
  useEffect(() => {
    const currentKey = getApiKey();
    if (currentKey) {
      setApiKey(currentKey);
      loadApiKeys();
      loadPrivacySettings();
    }
  }, []);

  const loadPrivacySettings = async () => {
    try {
      const response = await fetch('/api/ml/privacy', {
        headers: {
          'X-API-Key': getApiKey() || ''
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPrivacySettings({
          allow_training_data: data.allow_training_data,
          training_consent_at: data.training_consent_at
        });
      }
    } catch (error) {
      console.error('Failed to load privacy settings:', error);
    }
  };

  const loadApiKeys = async () => {
    try {
      const keys = await listAPIKeys();
      setApiKeys(keys);
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  };

  // Filter keys based on showInactive toggle
  const displayedKeys = showInactive 
    ? apiKeys 
    : apiKeys.filter(key => key.is_active);

  const handleSaveApiKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      toast.error('API key cannot be empty');
      return;
    }
    saveApiKey(apiKey);
    toast.success('API key saved successfully');
    loadApiKeys();
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!user) {
      toast.error('You must be logged in to create API keys');
      return;
    }

    if (!newKeyName.trim()) {
      toast.error('Key name cannot be empty');
      return;
    }
    
    setIsLoading(true);
    try {
      // Debug: Check if user is authenticated
      console.log('[DEBUG] Creating API key...');
      console.log('[DEBUG] User:', user);
      console.log('[DEBUG] Has API key:', !!getApiKey());
      
      const newKey = await createAPIKey({ name: newKeyName });
      if (newKey.api_key) {
        // Only save to localStorage if no key exists yet (first key)
        const existingKey = getApiKey();
        const isFirstKey = !existingKey || existingKey.trim() === '';
        
        if (isFirstKey) {
          saveApiKey(newKey.api_key);
          setApiKey(newKey.api_key);
          toast.success('API key created and activated! This is your first key.');
        } else {
          // Don't auto-activate additional keys - let user decide
          toast.success('API key created! Copy it now - it won\'t be shown again.');
        }
        
        // Store temporarily to show in UI with clear timeout
        setNewlyCreatedKey(newKey.api_key);
        setTimeout(() => setNewlyCreatedKey(null), 60000); // Clear after 1 minute
        setNewKeyName('');
        
        // Reload keys list after small delay to ensure database commit
        setTimeout(() => loadApiKeys(), 500);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create API key');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to deactivate this API key?')) return;
    
    setIsLoading(true);
    try {
      await deleteAPIKey(keyId);
      toast.success('API key deactivated');
      
      // Reload the keys list after small delay to ensure database commit
      setTimeout(() => loadApiKeys(), 300);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to deactivate API key');
    } finally {
      setIsLoading(false);
    }
  };

  const handleActivateKey = (keyId: string, keyName: string) => {
    // Can't actually activate since we don't have the full key value
    // User needs to copy it when created
    toast.error('API keys can only be copied when first created. Please create a new key if needed.');
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      toast.success('Signed out successfully');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to sign out');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('API key copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleTrainingData = async () => {
    if (!privacySettings) return;
    
    setIsUpdatingPrivacy(true);
    try {
      const response = await fetch('/api/ml/privacy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': getApiKey() || ''
        },
        body: JSON.stringify({
          allow_training_data: !privacySettings.allow_training_data
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setPrivacySettings({
          allow_training_data: data.allow_training_data,
          training_consent_at: data.training_consent_at
        });
        toast.success(data.message);
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to update privacy settings');
      }
    } catch (error) {
      toast.error('Failed to update privacy settings');
    } finally {
      setIsUpdatingPrivacy(false);
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
          <span className="font-mono-display text-sm text-foreground">Settings</span>
        </div>
      </header>

      <div className="container px-4 py-6">
        <div className="flex gap-6">
          {/* Sidebar Navigation */}
          <aside className="w-56 shrink-0">
            <nav className="glass-card p-3 border border-border/50">
              <div className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground px-3 py-2">
                Settings
              </div>
              <button
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md bg-primary/10 text-primary font-mono-display text-sm"
              >
                <Key className="h-4 w-4" />
                API
              </button>
              
              <div className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground px-3 py-2 mt-4">
                Developer
              </div>
              <Link
                to="/sandbox"
                className="w-full flex items-center gap-2 px-3 py-2 rounded-md hover:bg-secondary/50 text-foreground font-mono-display text-sm transition-colors"
              >
                <Beaker className="h-4 w-4" />
                Sandbox
              </Link>
            </nav>

            <Link
              to="/"
              className="flex items-center gap-2 mt-4 px-3 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            <div className="glass-card p-6 border border-border/50">
              <div className="mb-6">
                <h1 className="font-mono-display text-lg font-semibold text-foreground mb-1">
                  API Configuration
                </h1>
                <p className="text-sm text-muted-foreground">
                  Manage your API keys and integrations
                </p>
              </div>

              <form onSubmit={handleSaveApiKey} className="space-y-5 max-w-lg">
                <div className="space-y-2">
                  <Label htmlFor="apiKey" className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
                    Active API Key
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      id="apiKey"
                      type="password"
                      placeholder="No key set - create one below"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="bg-secondary/30 border-border/50 focus:border-primary/50 font-mono-display flex-1"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => apiKey && copyToClipboard(apiKey)}
                      disabled={!apiKey}
                    >
                      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    This is the API key currently being used for requests. You can paste a different key here to switch between keys.
                  </p>
                </div>

                <Button type="submit" className="font-mono-display">
                  Update Active Key
                </Button>
              </form>

              {/* Privacy Settings Section */}
              <div className="mt-8 border-t border-border/50 pt-6">
                <h2 className="font-mono-display text-lg font-semibold text-foreground mb-2">
                  Privacy & Data Usage
                </h2>
                <p className="text-sm text-muted-foreground mb-4">
                  Control how your data is used to improve our machine learning models
                </p>

                {privacySettings && (
                  <div className="max-w-lg">
                    <div className="flex items-start gap-4 p-4 rounded-md bg-secondary/20 border border-border/30">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Lock className="h-4 w-4 text-muted-foreground" />
                          <span className="font-mono-display text-sm font-semibold text-foreground">
                            Training Data Consent
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mb-3">
                          {privacySettings.allow_training_data
                            ? 'Your analysis data is being used to improve threat detection accuracy. You can opt out anytime.'
                            : 'Your data is NOT being used for training. Only you have access to your private analysis data.'}
                        </p>
                        
                        {privacySettings.training_consent_at && (
                          <p className="text-xs text-muted-foreground/70 mb-3">
                            Last updated: {new Date(privacySettings.training_consent_at).toLocaleString()}
                          </p>
                        )}

                        <Button
                          onClick={handleToggleTrainingData}
                          disabled={isUpdatingPrivacy}
                          variant={privacySettings.allow_training_data ? "destructive" : "default"}
                          size="sm"
                          className="font-mono-display"
                        >
                          {isUpdatingPrivacy
                            ? 'Updating...'
                            : privacySettings.allow_training_data
                            ? 'Disable Training Data'
                            : 'Enable Training Data'}
                        </Button>
                      </div>
                      
                      <div className={`mt-1 px-3 py-1 rounded text-xs font-mono-display ${
                        privacySettings.allow_training_data
                          ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                          : 'bg-muted text-muted-foreground border border-border/50'
                      }`}>
                        {privacySettings.allow_training_data ? 'Enabled' : 'Disabled'}
                      </div>
                    </div>

                    <div className="mt-4 p-3 rounded-md bg-blue-500/10 border border-blue-500/30">
                      <p className="text-xs text-blue-400">
                        <strong>ℹ️ How it works:</strong>
                      </p>
                      <ul className="mt-2 space-y-1 text-xs text-blue-400/80">
                        <li>• When enabled, text features (not raw text) are stored for model training</li>
                        <li>• Your data remains encrypted and isolated to your account</li>
                        <li>• Helps improve detection accuracy through machine learning</li>
                        <li>• You can disable this at any time</li>
                        <li>• Only applies to future analyses (doesn't affect past data)</li>
                      </ul>
                    </div>
                  </div>
                )}

                {!privacySettings && (
                  <div className="text-sm text-muted-foreground">
                    Loading privacy settings...
                  </div>
                )}
              </div>

              <div className="mt-8 border-t border-border/50 pt-6">
                <h2 className="font-mono-display text-lg font-semibold text-foreground mb-4">
                  Create New API Key
                </h2>
                <div className="mb-4 p-3 rounded-md bg-blue-500/10 border border-blue-500/30">
                  <p className="text-xs text-blue-400">
                    💡 <strong>Important:</strong> API keys are only shown once when created. Make sure to copy and save your key immediately!
                  </p>
                </div>
                <form onSubmit={handleCreateKey} className="space-y-4 max-w-lg">
                  <div className="space-y-2">
                    <Label htmlFor="newKeyName" className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
                      Key Name
                    </Label>
                    <Input
                      id="newKeyName"
                      type="text"
                      placeholder="e.g., Production Key"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      className="bg-secondary/30 border-border/50 focus:border-primary/50 font-mono-display"
                    />
                  </div>
                  <Button type="submit" disabled={isLoading} className="font-mono-display">
                    {isLoading ? 'Creating...' : 'Create New Key'}
                  </Button>
                </form>
              </div>

              {(newlyCreatedKey || apiKeys.length > 0) && (
                <div className="mt-8 border-t border-border/50 pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="font-mono-display text-lg font-semibold text-foreground">
                      Your API Keys
                    </h2>
                    {apiKeys.some(k => !k.is_active) && (
                      <button
                        onClick={() => setShowInactive(!showInactive)}
                        className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showInactive ? '✓ Showing All' : 'Show Inactive Keys'}
                      </button>
                    )}
                  </div>

                  {/* Show newly created key */}
                  {newlyCreatedKey && (
                    <div className="mb-4 p-4 rounded-md bg-primary/10 border border-primary/30">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="font-mono-display text-sm font-semibold text-primary mb-2">
                            🔑 New API Key Created!
                          </div>
                          <div className="text-xs text-muted-foreground mb-2">
                            Copy this key now - it won't be shown again for security reasons.
                          </div>
                          <div className="flex gap-2 items-center">
                            <code className="flex-1 px-3 py-2 bg-background/50 border border-border/50 rounded text-xs font-mono break-all">
                              {newlyCreatedKey}
                            </code>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => copyToClipboard(newlyCreatedKey)}
                            >
                              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {displayedKeys.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                      {showInactive ? 'No inactive keys found' : 'No active API keys yet'}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {displayedKeys.map((key) => {
                        const isCurrentKey = apiKey && key.last_used_at; // Approximate check
                        return (
                          <div
                            key={key.id}
                            className={`flex items-center justify-between p-4 rounded-md ${
                              !key.is_active
                                ? 'bg-muted/30 border-muted opacity-60'
                                : isCurrentKey 
                                  ? 'bg-primary/5 border-primary/30' 
                                  : 'bg-secondary/20 border-border/30'
                            } border`}
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <div className="font-mono-display text-sm font-semibold text-foreground">
                                  {key.name}
                                </div>
                                {!key.is_active && (
                                  <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                                    Inactive
                                  </span>
                                )}
                                {key.is_active && isCurrentKey && (
                                  <span className="flex items-center gap-1 text-xs text-primary">
                                    <CheckCircle2 className="h-3 w-3" />
                                    In Use
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-muted-foreground mt-1">
                                Created: {new Date(key.created_at).toLocaleDateString()}
                                {key.last_used_at && ` • Last used: ${new Date(key.last_used_at).toLocaleDateString()}`}
                              </div>
                              <div className="text-xs text-muted-foreground/70 mt-1">
                                Key ID: {key.id}
                              </div>
                            </div>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => handleDeleteKey(key.id)}
                              disabled={!key.is_active}
                            >
                              {key.is_active ? 'Deactivate' : 'Inactive'}
                            </Button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Key Management Help */}
              <div className="mt-8 p-4 rounded-md bg-muted/30 border border-border/30">
                <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-3">
                  🔐 Managing Multiple API Keys
                </h3>
                <ul className="space-y-2 text-xs text-muted-foreground">
                  <li>• <strong>First Key:</strong> Automatically activated and saved when created</li>
                  <li>• <strong>Additional Keys:</strong> Must be copied immediately (shown for 1 minute only)</li>
                  <li>• <strong>Switch Keys:</strong> Paste a different key in "Active API Key" field and click "Update"</li>
                  <li>• <strong>Security:</strong> Keys are only displayed once at creation for security</li>
                  <li>• <strong>Per Account:</strong> Each user account has separate, isolated API keys</li>
                  <li>• <strong>Deactivate:</strong> Deactivated keys are hidden by default (click "Show Inactive Keys" to view)</li>
                </ul>
              </div>

              <div className="mt-8 p-4 rounded-md bg-secondary/20 border border-border/30">
                <h3 className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground mb-2">
                  Backend Status
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="font-mono-display text-2xl font-semibold text-foreground">
                      {apiKey ? 'Connected' : 'No Key'}
                    </div>
                    <div className="text-xs text-muted-foreground">Connection Status</div>
                  </div>
                  <div>
                    <div className="font-mono-display text-2xl font-semibold text-foreground">
                      {apiKeys.filter(k => k.is_active).length}
                    </div>
                    <div className="text-xs text-muted-foreground">Active API Keys</div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default Settings;
