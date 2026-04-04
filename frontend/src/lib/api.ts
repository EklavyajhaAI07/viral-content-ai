import axios, { AxiosError } from "axios";
import type {
  AuthResponse,
  TrendResponse,
  HookResponse,
  CaptionResponse,
  HashtagResponse,
  ViralityResponse,
  ThumbnailResponse,
  StrategyResponse,
} from "@/types";

// ─── Axios Instance ───────────────────────────────────────────────────────────

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
  headers: { "Content-Type": "application/json" },
});

// ─── Token helper ─────────────────────────────────────────────────────────────

const getToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
};

// ─── Request interceptor — attach JWT on every request ───────────────────────

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Response interceptor — auto-logout on 401 ───────────────────────────────

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);


// ─── AUTH ─────────────────────────────────────────────────────────────────────
// Backend RegisterRequest: { email, name, password }
// Backend LoginRequest:    { email, password }
// Both return plain JSON — no form-encoding needed.

export const authAPI = {
  register: async (data: {
    email: string;
    name: string;
    password: string;
  }): Promise<AuthResponse> => {
    const res = await api.post("/api/auth/register", {
      email: data.email,
      name: data.name,
      password: data.password,
    });
    return res.data;
  },

  login: async (data: {
    email: string;
    password: string;
  }): Promise<AuthResponse> => {
    const res = await api.post("/api/auth/login", {
      email: data.email,
      password: data.password,
    });
    return res.data;
  },

  getMe: async (): Promise<AuthResponse["user"]> => {
    const res = await api.get("/api/auth/me");
    return res.data;
  },
};


// ─── TRENDS ───────────────────────────────────────────────────────────────────
// GET /api/trends?topic=&platform=

export const trendsAPI = {
  discover: async (data: {
    topic: string;
    platform?: string;
  }): Promise<TrendResponse> => {
    const res = await api.get("/api/trends", {
      params: { topic: data.topic, platform: data.platform ?? "all" },
    });
    return res.data;
  },
};


// ─── CONTENT ──────────────────────────────────────────────────────────────────

export const contentAPI = {

  generateHook: async (data: {
    topic: string;
    platform?: string;
    tone?: string;
    target_audience?: string;
  }): Promise<HookResponse> => {
    const res = await api.post("/api/content/hook", data);
    return res.data;
  },

  generateCaption: async (data: {
    topic: string;
    platform?: string;
    tone?: string;
    target_audience?: string;
    hook?: string;
  }): Promise<CaptionResponse> => {
    const res = await api.post("/api/content/caption", data);
    return res.data;
  },

  generateHashtags: async (data: {
    topic: string;
    platform?: string;
  }): Promise<HashtagResponse> => {
    const res = await api.post("/api/content/hashtags", data);
    return res.data;
  },

  predictVirality: async (data: {
    topic: string;
    platform?: string;
    caption?: string;
    hashtags?: string;
  }): Promise<ViralityResponse> => {
    const res = await api.post("/api/content/predict-virality", data);
    return res.data;
  },

  generateThumbnail: async (data: {
    topic: string;
    platform?: string;
    tone?: string;
  }): Promise<ThumbnailResponse> => {
    const res = await api.post("/api/content/thumbnail", data);
    return res.data;
  },
};


// ─── STRATEGY ─────────────────────────────────────────────────────────────────
// POST /api/strategy/generate

export const strategyAPI = {
  generate: async (data: {
    topic: string;
    platform?: string;
    virality_score?: number;
  }): Promise<StrategyResponse> => {
    const res = await api.post("/api/strategy/generate", data);
    return res.data;
  },
};


// ─── HEALTH ───────────────────────────────────────────────────────────────────

export const healthAPI = {
  check: async () => {
    const res = await api.get("/health");
    return res.data;
  },
};


// ─── ERROR HANDLER ────────────────────────────────────────────────────────────

type ApiErrorPayload = {
  detail?: string;
  message?: string;
};

export function getApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong.",
): string {
  const axiosError = error as AxiosError<ApiErrorPayload>;
  return (
    axiosError.response?.data?.detail ||
    axiosError.response?.data?.message ||
    axiosError.message ||
    fallback
  );
}

export default api;