/**
 * Hook for real-time threat monitoring with Supabase
 */
import { useState, useEffect, useCallback } from 'react';
import { subscribeToThreats, fetchRecentThreats, type ThreatRecord, isSupabaseConfigured } from '@/services/supabase';
import { getStats, type StatsResponse } from '@/services/api';

export interface ThreatStats {
  total: number;
  high: number;
  medium: number;
  low: number;
  recent: ThreatRecord[];
}

export const useRealtimeThreats = (userId?: string) => {
  const [threats, setThreats] = useState<ThreatRecord[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isConfigured, setIsConfigured] = useState(false);

  // Load initial data
  const loadInitialData = useCallback(async () => {
    setIsLoading(true);
    try {
      // Load recent threats
      const recentThreats = await fetchRecentThreats(20, userId);
      setThreats(recentThreats);

      // Load stats from backend
      const statsData = await getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Subscribe to real-time updates
  useEffect(() => {
    setIsConfigured(isSupabaseConfigured());
    
    if (!isSupabaseConfigured()) {
      setIsLoading(false);
      return;
    }

    loadInitialData();

    // Poll for updates every 2 seconds instead of realtime
    const pollInterval = setInterval(async () => {
      try {
        const recentThreats = await fetchRecentThreats(20, userId);
        setThreats(recentThreats);
        
        const statsData = await getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000);

    return () => {
      clearInterval(pollInterval);
    };
  }, [userId, loadInitialData]);

  // Refresh data manually
  const refresh = useCallback(async () => {
    await loadInitialData();
  }, [loadInitialData]);

  return {
    threats,
    stats,
    isLoading,
    isConfigured,
    refresh,
  };
};
