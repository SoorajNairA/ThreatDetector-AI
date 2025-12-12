/**
 * Hook for managing backend connection and stats
 */
import { useState, useEffect, useCallback } from 'react';
import { checkHealth, getStats, type StatsResponse } from '@/services/api';

export const useBackend = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  // Check backend health
  const checkConnection = useCallback(async () => {
    setIsChecking(true);
    try {
      await checkHealth();
      setIsConnected(true);
      return true;
    } catch (error) {
      setIsConnected(false);
      return false;
    } finally {
      setIsChecking(false);
    }
  }, []);

  // Load stats
  const loadStats = useCallback(async () => {
    setIsLoadingStats(true);
    try {
      const data = await getStats();
      setStats(data);
      return data;
    } catch (error) {
      console.error('Failed to load stats:', error);
      return null;
    } finally {
      setIsLoadingStats(false);
    }
  }, []);

  // Check connection on mount
  useEffect(() => {
    checkConnection();
  }, [checkConnection]);

  return {
    isConnected,
    isChecking,
    stats,
    isLoadingStats,
    checkConnection,
    loadStats,
  };
};
