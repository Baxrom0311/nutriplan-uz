import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

const rawApiBase = import.meta.env.VITE_API_BASE_URL ?? "/api";
const API_BASE = rawApiBase.replace(/\/+$/, "");

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export const clearAuthTokens = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

type PendingRequest = {
  resolve: (token: string) => void;
  reject: (error: AxiosError) => void;
};

let isRefreshing = false;
let failedQueue: PendingRequest[] = [];

const setAuthorizationHeader = (config: RetryableRequestConfig, token: string) => {
  config.headers.Authorization = `Bearer ${token}`;
};

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((p) => {
    if (error) p.reject(error);
    else if (token) p.resolve(token);
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          setAuthorizationHeader(originalRequest, token);
          return api(originalRequest);
        });
      }
      originalRequest._retry = true;
      isRefreshing = true;
      const refresh = localStorage.getItem("refresh_token");
      if (!refresh) {
        clearAuthTokens();
        window.location.assign("/login");
        return Promise.reject(error);
      }
      try {
        const { data } = await axios.post<{ access: string }>(`${API_BASE}/auth/refresh/`, { refresh });
        localStorage.setItem("access_token", data.access);
        processQueue(null, data.access);
        setAuthorizationHeader(originalRequest, data.access);
        return api(originalRequest);
      } catch (refreshError) {
        const refreshAxiosError = refreshError as AxiosError;
        processQueue(refreshAxiosError, null);
        clearAuthTokens();
        window.location.assign("/login");
        return Promise.reject(refreshAxiosError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export default api;
