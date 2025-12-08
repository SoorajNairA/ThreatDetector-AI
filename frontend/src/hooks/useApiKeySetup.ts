/**
 * Hook for managing API key setup and validation
 */
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { getApiKey, createAPIKey, setApiKey as saveApiKey } from '@/services/api';
import { toast } from 'sonner';

export const useApiKeySetup = () => {
  const { user } = useAuth();
  const [hasApiKey, setHasApiKey] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkApiKey = () => {
      const key = getApiKey();
      setHasApiKey(!!key);
      setIsChecking(false);
    };

    checkApiKey();
  }, []);

  const createDefaultApiKey = async () => {
    if (!user) {
      toast.error('You must be logged in to create an API key');
      return false;
    }

    setIsCreating(true);
    try {
      const newKey = await createAPIKey({ name: 'Default Key' });
      if (newKey.api_key) {
        saveApiKey(newKey.api_key);
        setHasApiKey(true);
        toast.success('API key created successfully!');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to create API key:', error);
      toast.error('Failed to create API key. Please try again from Settings.');
      return false;
    } finally {
      setIsCreating(false);
    }
  };

  return {
    hasApiKey,
    isChecking,
    isCreating,
    createDefaultApiKey,
  };
};
