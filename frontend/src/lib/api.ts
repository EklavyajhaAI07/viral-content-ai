import axios, { AxiosError } from "axios";
import type {
  AuthResponse,
  TrendResponse,
  ContentResponse,
  ViralityResponse,
  StrategyResponse,
} from "@/types";

// ✅ Base URL (env + fallback)
const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ✅ Axios instance
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Helper for token (SAFE for SSR)
const getToken = () => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
};

// ✅ Attach token automatically
api.interceptors.request.use((config) => {
  const token = getToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ─────────────────────────────
// 🔐 AUTH API
// ─────────────────────────────
export const authAPI = {
  register: async (data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }): Promise<AuthResponse> => {
    const res = await api.post("/api/auth/register", data);
    return res.data;
  },

  login: async (data: {
    email: string;
    password: string;
  }): Promise<AuthResponse> => {
    const res = await api.post("/api/auth/login", data);
    return res.data;
  },

  getMe: async () => {
    const res = await api.get("/api/auth/me");
    return res.data;
  },
};

// ─────────────────────────────
// 📈 TRENDS API
// ─────────────────────────────
export const trendsAPI = {
  discover: async (data: {
    topic: string;
    platform?: string;
  }): Promise<TrendResponse> => {
    const res = await api.post("/api/trends/discover", data);
    return res.data;
  },
};

// ─────────────────────────────
// ✍️ CONTENT API
// ─────────────────────────────
export const contentAPI = {
  generate: async (data: {
    topic: string;
    platform?: string;
    tone?: string;
    target_audience?: string;
  }): Promise<ContentResponse> => {
    const res = await api.post("/api/content/generate", data);
    return res.data;
  },

  predictVirality: async (data: {
    topic: string;
    caption?: string;
    hashtags?: string;
    platform?: string;
  }): Promise<ViralityResponse> => {
    const res = await api.post("/api/content/predict-virality", data);
    return res.data;
  },
};

// ─────────────────────────────
// 📊 STRATEGY API
// ─────────────────────────────
export const strategyAPI = {
  generate: async (data: {
    topic: string;
    platform?: string;
  }): Promise<StrategyResponse> => {
    const res = await api.post("/api/strategy/generate", data);
    return res.data;
  },
};

// ─────────────────────────────
// ❤️ HEALTH API
// ─────────────────────────────
export const healthAPI = {
  check: async () => {
    const res = await api.get("/api/health");
    return res.data;
  },
};

// ─────────────────────────────
// ❌ ERROR HANDLER
// ─────────────────────────────
type ApiErrorPayload = {
  detail?: string;
  message?: string;
};

export function getApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong.",
) {
  const axiosError = error as AxiosError<ApiErrorPayload>;

  return (
    axiosError.response?.data?.detail ||
    axiosError.response?.data?.message ||
    axiosError.message ||
    fallback
  );
}

export default api;