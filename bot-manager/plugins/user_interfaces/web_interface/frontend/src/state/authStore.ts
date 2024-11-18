import type { StoreApi, UseBoundStore } from "zustand";
import { create } from "zustand";

interface AuthState {
  isLoggedIn: boolean | undefined; // undefined to indicate loading state
  backendUrl: string;
  frontendPath: string;
  routes: {
    home: string;
    login: string;
    logout: string;
    config: string;
  };
  logout: () => Promise<void>;
  checkLogin: () => Promise<void>;
}

const hostName = window.location.hostname;
const protocol = window.location.protocol;
const backendUrl = `${protocol}//${hostName}:5000/api`;
const frontendPath = "/web";

interface AuthCheckResponse {
  logged_in: boolean;
}

export const useAuthStore: UseBoundStore<StoreApi<AuthState>> =
  create<AuthState>((set, get) => ({
    isLoggedIn: undefined, // initially loading
    backendUrl,
    frontendPath,
    routes: {
      home: `${frontendPath}/`,
      login: `${frontendPath}/login`,
      logout: `${backendUrl}/logout`,
      config: `${frontendPath}/config`,
    },
    logout: async (): Promise<void> => {
      const state = get();
      await fetch(state.routes.logout);
      set({ isLoggedIn: false });
      console.log("Logged out");
    },
    checkLogin: async (): Promise<void> => {
      try {
        const response = await fetch(`${backendUrl}/auth-check`, {
          credentials: "include",
        });
        const data: AuthCheckResponse =
          (await response.json()) as AuthCheckResponse;
        set({ isLoggedIn: data.logged_in });
      } catch (err) {
        set({ isLoggedIn: false });
      }
    },
  }));
