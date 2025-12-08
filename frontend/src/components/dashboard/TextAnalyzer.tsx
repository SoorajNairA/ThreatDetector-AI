/**
 * Text input component for threat analysis
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';

interface TextAnalyzerProps {
  onSubmit: (text: string) => void;
  isAnalyzing: boolean;
}

export const TextAnalyzer = ({ onSubmit, isAnalyzing }: TextAnalyzerProps) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      onSubmit(text);
    }
  };

  const sampleTexts = [
    'Urgent! Your account has been compromised. Click here to verify: http://bit.ly/verify123',
    'Congratulations! You have won $10,000. Claim your prize now by sending your bank details.',
    'Hey, just checking in. How was your weekend?',
  ];

  const loadSample = (sample: string) => {
    setText(sample);
  };

  return (
    <div className="glass-card p-6 border border-border/50">
      <div className="mb-4">
        <h2 className="font-mono-display text-lg font-semibold text-foreground mb-2">
          Analyze Text
        </h2>
        <p className="text-sm text-muted-foreground">
          Enter text to analyze for potential threats
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="text" className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
            Text Content
          </Label>
          <Textarea
            id="text"
            placeholder="Enter text to analyze..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            className="resize-none"
            disabled={isAnalyzing}
          />
        </div>

        <div className="flex items-center gap-2">
          <Button
            type="submit"
            disabled={!text.trim() || isAnalyzing}
            className="flex-1"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              'Analyze'
            )}
          </Button>
        </div>

        <div className="space-y-2">
          <Label className="font-mono-display text-xs uppercase tracking-wider text-muted-foreground">
            Sample Texts
          </Label>
          <div className="space-y-2">
            {sampleTexts.map((sample, index) => (
              <button
                key={index}
                type="button"
                onClick={() => loadSample(sample)}
                className="w-full text-left p-3 rounded-md bg-secondary/30 hover:bg-secondary/50 border border-border/30 text-xs text-muted-foreground transition-colors"
                disabled={isAnalyzing}
              >
                {sample.substring(0, 80)}...
              </button>
            ))}
          </div>
        </div>
      </form>
    </div>
  );
};
