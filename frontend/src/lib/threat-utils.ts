export interface ThreatData {
  name: string;
  value: number;
}

export interface BreakdownItem {
  category: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  score: number;
}

export interface Finding {
  id: string;
  type: 'safe' | 'warning' | 'danger' | 'info';
  title: string;
  description: string;
  timestamp: string;
}

export interface TrendPoint {
  time: string;
  value: number;
}

export const generateRandomThreatData = (): ThreatData[] => {
  return [
    { name: 'Malware', value: Math.floor(Math.random() * 100) },
    { name: 'Phishing', value: Math.floor(Math.random() * 100) },
    { name: 'Injection', value: Math.floor(Math.random() * 100) },
    { name: 'XSS', value: Math.floor(Math.random() * 100) },
    { name: 'DDoS', value: Math.floor(Math.random() * 100) },
    { name: 'Ransomware', value: Math.floor(Math.random() * 100) },
  ];
};

export const generateRandomRiskScore = (): number => {
  return Math.floor(Math.random() * 100);
};

export const getSeverityFromScore = (score: number): 'low' | 'medium' | 'high' | 'critical' => {
  if (score <= 25) return 'low';
  if (score <= 50) return 'medium';
  if (score <= 75) return 'high';
  return 'critical';
};

export const getSeverityLabel = (score: number): string => {
  if (score <= 25) return 'LOW';
  if (score <= 50) return 'MODERATE';
  if (score <= 75) return 'HIGH';
  return 'CRITICAL';
};

export const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'low':
      return 'text-success';
    case 'medium':
      return 'text-chart-1';
    case 'high':
      return 'text-warning';
    case 'critical':
      return 'text-danger';
    default:
      return 'text-muted-foreground';
  }
};

export const generateBreakdownData = (): BreakdownItem[] => {
  const categories = [
    { category: 'Network Security', description: 'Firewall configuration and network traffic analysis' },
    { category: 'Data Protection', description: 'Encryption status and data handling policies' },
    { category: 'Access Control', description: 'Authentication mechanisms and permission structures' },
    { category: 'Vulnerability Scan', description: 'Known CVEs and security patches status' },
    { category: 'Compliance', description: 'Regulatory requirements and audit trails' },
    { category: 'Incident Response', description: 'Detection capabilities and response procedures' },
  ];

  return categories.map((item) => {
    const score = Math.floor(Math.random() * 100);
    return {
      ...item,
      score,
      severity: getSeverityFromScore(score),
    };
  });
};

export const generateFindings = (riskScore: number): Finding[] => {
  const findings: Finding[] = [];
  const timestamp = new Date().toLocaleTimeString();

  if (riskScore < 25) {
    findings.push({
      id: '1',
      type: 'safe',
      title: 'System Secure',
      description: 'No critical threats detected in the current scan.',
      timestamp,
    });
  } else if (riskScore < 50) {
    findings.push({
      id: '1',
      type: 'warning',
      title: 'Minor Vulnerabilities',
      description: 'Some non-critical issues require attention.',
      timestamp,
    });
    findings.push({
      id: '2',
      type: 'info',
      title: 'Recommendation',
      description: 'Consider updating security patches.',
      timestamp,
    });
  } else if (riskScore < 75) {
    findings.push({
      id: '1',
      type: 'danger',
      title: 'Active Threats Detected',
      description: 'Multiple security concerns identified.',
      timestamp,
    });
    findings.push({
      id: '2',
      type: 'warning',
      title: 'Elevated Risk Level',
      description: 'Immediate review recommended.',
      timestamp,
    });
  } else {
    findings.push({
      id: '1',
      type: 'danger',
      title: 'Critical Alert',
      description: 'Severe security breach potential detected.',
      timestamp,
    });
    findings.push({
      id: '2',
      type: 'danger',
      title: 'Immediate Action Required',
      description: 'System isolation recommended.',
      timestamp,
    });
    findings.push({
      id: '3',
      type: 'warning',
      title: 'Data at Risk',
      description: 'Sensitive information may be exposed.',
      timestamp,
    });
  }

  return findings;
};

export const getCurrentTimeLabel = (): string => {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};
