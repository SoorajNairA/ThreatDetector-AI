/**
 * Supabase client for real-time data subscriptions
 */
import { createClient, RealtimeChannel } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Create Supabase client if credentials are available
export const supabase = supabaseUrl && supabaseAnonKey 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

// Types for database schema
export interface ThreatRecord {
  id: string;
  text: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  risk_score: number;
  intent: string;
  ai_generated: boolean;
  timestamp: string;
  actor?: string;
  user_id?: string;
}

// Subscribe to real-time threat updates
export const subscribeToThreats = (
  callback: (threat: ThreatRecord) => void,
  userId?: string
): RealtimeChannel | null => {
  if (!supabase) return null;

  const channel = supabase
    .channel('threats-changes')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'threats',
        filter: userId ? `user_id=eq.${userId}` : undefined,
      },
      (payload) => {
        callback(payload.new as ThreatRecord);
      }
    )
    .subscribe();

  return channel;
};

// Fetch recent threats
export const fetchRecentThreats = async (
  limit: number = 10,
  userId?: string
): Promise<ThreatRecord[]> => {
  if (!supabase) {
    console.log('[Supabase] Client not configured');
    return [];
  }

  try {
    console.log('[Supabase] Fetching threats...', { limit, userId });
    
    let query = supabase
      .from('threats')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit);

    if (userId) {
      query = query.eq('user_id', userId);
    }

    const { data, error } = await query;

    if (error) {
      console.error('[Supabase] Query error:', error);
      throw error;
    }
    
    console.log('[Supabase] Fetched threats:', data?.length || 0);
    return data || [];
  } catch (error) {
    console.error('[Supabase] Failed to fetch threats:', error);
    return [];
  }
};

// Check if Supabase is configured
export const isSupabaseConfigured = (): boolean => {
  return Boolean(supabaseUrl && supabaseAnonKey);
};
