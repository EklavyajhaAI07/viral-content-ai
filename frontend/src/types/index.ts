// ── Auth ──
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  plan: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ── Trends ──
export interface TrendItem {
  topic: string;
  hashtags: string[];
  platforms: string[];
  velocity_score: number;
  niche: string;
  peak_prediction_hours: number;
  status: "emerging" | "peak" | "declining";
}

export interface TrendResponse {
  status: string;
  source: string;
  data: {
    topic: string;
    platform: string;
    trends: TrendItem[];
  };
  generated_at: string;
}

// ── Content ──
export interface ContentData {
  hook: string;
  caption: string;
  hashtags: {
    niche: string[];
    trending: string[];
    broad: string[];
  };
  cta: string;
  alternative_hooks: string[];
  best_posting_time: string;
  content_format: string;
  platform: string;
  tone: string;
}

export interface ContentResponse {
  status: string;
  source: string;
  data: ContentData;
  generated_at: string;
}

// ── Virality ──
export interface ViralityBreakdown {
  hook_strength: number;
  hashtag_relevance: number;
  trend_alignment: number;
  emotional_tone: number;
  posting_time_fit: number;
}

export interface ViralityData {
  virality_score: number;
  confidence: number;
  grade: string;
  breakdown: ViralityBreakdown;
  predicted_reach: number;
  predicted_engagement_rate: number;
  improvements: string[];
  rewritten_hook: string;
}

export interface ViralityResponse {
  status: string;
  source: string;
  data: ViralityData;
  generated_at: string;
}

// ── Strategy ──
export interface CalendarDay {
  day: string;
  date: string;
  platform: string;
  content_type: string;
  topic_angle: string;
  post_time: string;
  priority: string;
}

export interface StrategyData {
  topic: string;
  platform: string;
  calendar: CalendarDay[];
  repurposing_plan: Record<string, string>;
  growth_strategy: Record<string, { title: string; actions: string[] }>;
  content_gaps: Array<{ gap: string; opportunity: string; viral_potential: string }>;
  ab_tests: Array<{ element: string; variant_a: string; variant_b: string; metric: string }>;
  forecast_30_day: Record<string, string>;
}

export interface StrategyResponse {
  status: string;
  source: string;
  data: StrategyData;
  generated_at: string;
}
