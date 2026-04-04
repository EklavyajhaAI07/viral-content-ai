// ─── AUTH ─────────────────────────────────────────────────────────────────────

export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}


// ─── TRENDS ───────────────────────────────────────────────────────────────────
// GET /api/trends

export interface HashtagItem {
  tag: string;
  velocity: number;           // 0–100
  strongest_on: string;       // "instagram" | "tiktok" | etc.
  peak_in_hours: number;
}

export interface ViralAngle {
  angle: string;
  description: string;
  virality_score: number;     // 0–100
}

export interface TrendResponse {
  job_id: string;
  topic: string;
  platform: string;
  hashtags: HashtagItem[];
  viral_angles: ViralAngle[];
  niche_classification: string;
  overall_trend_velocity: number;
  has_real_data: boolean;
  status: string;
  cached: boolean;
  elapsed_seconds: number;
}


// ─── CONTENT: HOOK ────────────────────────────────────────────────────────────
// POST /api/content/hook

export interface HookResponse {
  job_id: string;
  topic: string;
  platform: string;
  hook: string;
  alternative_hooks: string[];  // always 3 items
  cta: string;
  format_recommendation: string;
  status: string;
  cached: boolean;
  elapsed_seconds: number;
}


// ─── CONTENT: CAPTION ─────────────────────────────────────────────────────────
// POST /api/content/caption

export interface CaptionResponse {
  job_id: string;
  topic: string;
  platform: string;
  caption: string;
  best_posting_time: string;
  word_count: number;
  status: string;
  cached: boolean;
  elapsed_seconds: number;
}


// ─── CONTENT: HASHTAGS ────────────────────────────────────────────────────────
// POST /api/content/hashtags

export interface HashtagResponse {
  job_id: string;
  topic: string;
  platform: string;
  niche: string[];      // 5 tags — under 500k posts
  trending: string[];   // 5 tags — 500k–5M posts
  broad: string[];      // 5 tags — 5M+ posts
  total_count: number;  // always 15
  status: string;
  cached: boolean;
  elapsed_seconds: number;
}


// ─── CONTENT: VIRALITY ────────────────────────────────────────────────────────
// POST /api/content/predict-virality

export interface ViralityBreakdown {
  hook_strength: number;
  hashtag_relevance: number;
  trend_alignment: number;
  emotional_tone: number;
  posting_time_fit: number;
}

export interface ViralityResponse {
  job_id: string;
  topic: string;
  platform: string;
  overall_score: number;        // 0–100
  grade: string;                // A+ | A | B+ | B | C+ | C | D | F
  confidence: number;           // 0.0–1.0
  predicted_reach: number;
  predicted_engagement_rate: number;
  breakdown: ViralityBreakdown;
  improvements: string[];       // always 3 items
  rewritten_hook: string;
  status: string;
  cached: boolean;
  elapsed_seconds: number;
}


// ─── CONTENT: THUMBNAIL ───────────────────────────────────────────────────────
// POST /api/content/thumbnail

export interface ThumbnailData {
  url: string;
  path: string;
  status: string;
  source: string;   // "stability" | "pollinations"
}

export interface ThumbnailResponse {
  job_id: string;
  topic: string;
  platform: string;
  thumbnail: ThumbnailData;
  status: string;
  elapsed_seconds: number;
}


// ─── STRATEGY ─────────────────────────────────────────────────────────────────
// POST /api/strategy/generate

export interface StrategyResponse {
  job_id: string;
  topic: string;
  platform: string;
  strategy: string;   // full markdown text from Strategist agent
  status: string;
  cached: boolean;
  elapsed_seconds: number;
}


// ─── SHARED ───────────────────────────────────────────────────────────────────

export type Platform =
  | "instagram"
  | "tiktok"
  | "youtube"
  | "linkedin"
  | "twitter"
  | "all";

export type Tone =
  | "engaging"
  | "exciting"
  | "professional"
  | "funny"
  | "inspirational"
  | "educational";

export type Grade = "A+" | "A" | "B+" | "B" | "C+" | "C" | "D" | "F";