import type { StoreApi, UseBoundStore } from "zustand";
import { create } from "zustand";
import { genSalt, hash } from "bcryptjs";
interface AuthState {
  backendUrl: string;
  frontendPath: string;
  routes: {
    frontend: {
      home: string;
      room: string;
      login: string;
      config: string;
    };
    backend: {
      login: string;
      logout: string;
    };
  };
  isLoggedIn: boolean | undefined; // undefined to indicate loading state
  requiresSetup: boolean | undefined; // undefined to indicate loading state
  login: (password: string) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  checkLogin: () => Promise<void>;

  config: Config | undefined;
  updateConfig: () => Promise<void>;
  fetchConfig: () => Promise<void>;
}

const hostName = window.location.hostname;
const protocol = window.location.protocol;
const backendUrl = `${protocol}//${hostName}:5000/api`;
const frontendPath = "/web";

export const useBotStore: UseBoundStore<StoreApi<AuthState>> =
  create<AuthState>(
    (set, get) =>
      ({
        backendUrl,
        frontendPath,
        routes: {
          frontend: {
            home: `${frontendPath}/`,
            login: `${frontendPath}/login`,
            room: `${frontendPath}/room`,
            config: `${frontendPath}/config`,
          },
          backend: {
            logout: `${backendUrl}/logout`,
            login: `${backendUrl}/login`,
          },
        },
        isLoggedIn: undefined, // initially loading
        requiresSetup: undefined,
        login: async (password: string): Promise<LoginResponse> => {
          const state = get();
          const salt: string = await genSalt(10);
          const hashedPassword: string = await hash(password, salt);
          const loginResponse = await fetch(state.routes.backend.login, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password: hashedPassword }),
          });
          const responseData = (await loginResponse.json()) as LoginResponse;
          if (responseData.success) {
            set({ isLoggedIn: true });
            console.log("Logged in");
          }
          return responseData;
        },
        logout: async (): Promise<void> => {
          const state = get();
          await fetch(state.routes.backend.logout, {
            credentials: "include",
          });
          set({ isLoggedIn: false });
          document.cookie = `session=;path=/;domain=${
            window.location.hostname
          };expires=Thu, 01 Jan 1970 00:00:01 GMT`;
          console.log("Logged out");
        },
        checkLogin: async (): Promise<void> => {
          try {
            const response = await fetch(`${backendUrl}/auth-check`, {
              credentials: "include",
            });
            const data: AuthCheckResponse =
              (await response.json()) as AuthCheckResponse;
            set({
              isLoggedIn: data.loggedIn,
              requiresSetup: data.requiresSetup,
            });
            if (data.loggedIn) {
              await get().fetchConfig();
            }
          } catch (err) {
            console.error(err);
            set({ isLoggedIn: false });
          }
        },
        config: undefined,
        updateConfig: async (): Promise<void> => {
          const response = await fetch(`${backendUrl}/config`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(get().config),
            // Include cookies for authentication
            credentials: "include",
          });
          const responseData: Config = (await response.json()) as Config;
          set({ config: responseData });
        },
        fetchConfig: async (): Promise<void> => {
          const response = await fetch(`${backendUrl}/config`, {
            // Include cookies for authentication
            credentials: "include",
          });
          const responseData: Config = (await response.json()) as Config;
          set({ config: responseData });
        },
      }) as AuthState,
  );

interface AuthCheckResponse {
  loggedIn: boolean;
  requiresSetup: boolean;
}

export interface LoginResponse {
  success: boolean;
  requiresPasswordReset?: boolean;
  message?: string;
}

export interface Config {
  bot_config: {
    id: string;
    profile_name: string;
    message_interface: {
      [key: string]: string;
    };
    web_interface: {
      [key: string]: string;
    };
    bot: {
      [key: string]: string;
    };
  };
  bot_memory: {
    mind_map: string;
    // eslint-disable-next-line @typescript-eslint/ban-types
    periodic_summaries: {};
    messages: {
      [timestamp: string]: {
        content: string;
        role: "system" | "assistant" | "user";
      };
    };
  };
}
