import { create } from "zustand";
import api from "@/lib/api";
import type { UserProfile } from "@/lib/types";

interface AuthState {
  user: UserProfile | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { username: string; email: string; password: string; password2: string }) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  recalculate: () => Promise<void>;
  init: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: localStorage.getItem("access_token"),
  isLoading: true,

  init() {
    const token = localStorage.getItem("access_token");
    if (token) {
      set({ accessToken: token });
      api.get("/auth/me/").then(({ data }) => set({ user: data, isLoading: false })).catch(() => set({ isLoading: false }));
    } else {
      set({ isLoading: false });
    }
  },

  async login(email, password) {
    const { data } = await api.post("/auth/login/", { email, password });
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    set({ accessToken: data.access });
    const profile = await api.get("/auth/me/");
    set({ user: profile.data });
  },

  async register(body) {
    await api.post("/auth/register/", body);
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, accessToken: null });
  },

  async fetchProfile() {
    const { data } = await api.get("/auth/me/");
    set({ user: data });
  },

  async updateProfile(body) {
    const { data } = await api.patch("/auth/me/", body);
    set({ user: data });
  },

  async recalculate() {
    await api.post("/auth/me/calculate/");
    const { data } = await api.get("/auth/me/");
    set({ user: data });
  },
}));
