/**
 * Hook for managing text analysis with backend API
 */
import { useState, useCallback } from 'react';
import { analyzeText, type AnalyzeResponse } from '@/services/api';
import { toast } from 'sonner';

export interface UseAnalysisOptions {
  onSuccess?: (result: AnalyzeResponse) => void;
  onError?: (error: Error) => void;
}

export const useAnalysis = (options?: UseAnalysisOptions) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [lastResult, setLastResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const analyze = useCallback(async (text: string, actor?: string, sandbox?: boolean) => {
    if (!text.trim()) {
      const err = new Error('Text cannot be empty');
      setError(err);
      options?.onError?.(err);
      return null;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await analyzeText({ text, actor, sandbox });
      setLastResult(result);
      options?.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Analysis failed');
      setError(error);
      options?.onError?.(error);
      toast.error('Analysis failed', {
        description: error.message,
      });
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, [options]);

  return {
    analyze,
    isAnalyzing,
    lastResult,
    error,
  };
};
