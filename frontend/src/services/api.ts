/**
 * API service for backend communication
 */
import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Get API key from localStorage or environment
export const getApiKey = (): string | null => {
  // Try localStorage first (user's personal key)
  const storedKey = localStorage.getItem('api_key');
  if (storedKey && storedKey.trim() !== '') return storedKey;
  
  // Fall back to environment variable (dev only)
  return import.meta.env.VITE_API_KEY || null;
};

// Set API key in localStorage
export const setApiKey = (key: string): void => {
  localStorage.setItem('api_key', key);
};

// Remove API key from localStorage
export const clearApiKey = (): void => {
  localStorage.removeItem('api_key');
};

// Get Supabase Auth token
async function getAuthToken(): Promise<string | null> {
  if (!supabase) return null;
  
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token || null;
}

// Generic fetch wrapper with authentication
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const apiKey = getApiKey();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Add API key if available
  if (apiKey) {
    headers['x-api-key'] = apiKey;
  }
  
  // Also try to add Supabase Auth token (backend will use whichever is valid)
  const authToken = await getAuthToken();
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  // Debug logging
  console.log('[API Debug]', {
    endpoint,
    hasApiKey: !!apiKey,
    hasAuthToken: !!authToken,
    apiKeyPreview: apiKey ? `${apiKey.substring(0, 10)}...` : 'none'
  });
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

// ============================================================================
// HEALTH
// ============================================================================

export interface HealthResponse {
  status: string;
  timestamp?: string;
}

export const checkHealth = (): Promise<HealthResponse> => {
  return fetchAPI('/health');
};

// ============================================================================
// ANALYZE
// ============================================================================

export interface AnalyzeRequest {
  text: string;
  actor?: string;
  sandbox?: boolean;
}

export interface AnalysisDetails {
  ai_generated: boolean;
  ai_confidence: number;
  human_confidence: number;
  intent: string;
  intent_confidence: number;
  style_score: number;
  url_detected: boolean;
  url_score: number;
  domains: string[];
  keywords: string[];
  keyword_score: number;
}

export interface AnalyzeResponse {
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  analysis: AnalysisDetails;
  timestamp: string;
  message: string;
}

export const analyzeText = (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
  return fetchAPI('/analyze', {
    method: 'POST',
    body: JSON.stringify(request),
  });
};

// ============================================================================
// STATS
// ============================================================================

export interface StatsResponse {
  total: number;
  high: number;
  medium: number;
  low: number;
  actors: number;
  last: string | null;
}

export const getStats = (): Promise<StatsResponse> => {
  return fetchAPI('/stats');
};

// ============================================================================
// API KEYS
// ============================================================================

export interface CreateKeyRequest {
  name?: string;
}

export interface APIKeyResponse {
  id: string;
  api_key?: string; // Only present on creation
  name: string;
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
}

export const createAPIKey = (request: CreateKeyRequest): Promise<APIKeyResponse> => {
  return fetchAPI('/keys', {
    method: 'POST',
    body: JSON.stringify(request),
  });
};

export const listAPIKeys = (): Promise<APIKeyResponse[]> => {
  return fetchAPI('/keys');
};

export const deleteAPIKey = (keyId: string): Promise<{ message: string }> => {
  return fetchAPI(`/keys/${keyId}`, {
    method: 'DELETE',
  });
};
