// File: context/AuthContext.tsx
// Description: Keep the token, profile ID, and authenticated requests together.

import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { BASE_URL } from '../constants/api';

export type AuthFetch = (url: string, options?: RequestInit) => Promise<Response>;

type AuthContextValue = {
  token: string | null;
  profileId: number | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  authFetch: AuthFetch;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [profileId, setProfileId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Restore a saved session only after the API accepts its token and profile.
    (async () => {
      try {
        const savedToken = await AsyncStorage.getItem('auth_token');
        const savedProfileId = await AsyncStorage.getItem('profile_id');
        if (savedToken && savedProfileId) {
          const response = await fetch(`${BASE_URL}/api/profile/${savedProfileId}`, {
            headers: { Authorization: `Token ${savedToken}` },
          });
          if (response.status === 200) {
            const profile = await response.json();
            if (profile.id === Number(savedProfileId)) {
              // Profile pages are readable by other users; the feed verifies ownership.
              const feedResponse = await fetch(`${BASE_URL}/api/profile/${savedProfileId}/feed`, {
                headers: { Authorization: `Token ${savedToken}` },
              });
              if (feedResponse.status === 200) {
                setToken(savedToken);
                setProfileId(profile.id);
                return;
              }
            }
          }
        }
        await AsyncStorage.removeItem('auth_token');
        await AsyncStorage.removeItem('profile_id');
      } catch {
        // Leave a saved token available for a later retry after a connection error.
        setToken(null);
        setProfileId(null);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const login = async (username: string, password: string) => {
    const response = await fetch(`${BASE_URL}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username, password: password }),
    });
    if (response.status !== 200) {
      if (response.status === 401) throw new Error('Invalid credentials.');
      if (response.status === 403) throw new Error('This account does not have a profile.');
      throw new Error('Could not log in. Please try again.');
    }

    const data = await response.json();
    await AsyncStorage.setItem('auth_token', data.token);
    await AsyncStorage.setItem('profile_id', String(data.profile.id));
    setToken(data.token);
    setProfileId(data.profile.id);
  };

  const logout = async () => {
    setToken(null);
    setProfileId(null);
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('profile_id');
  };

  // Follow the PDF's wrapper: add the token and handle 401 in one place.
  const authFetch: AuthFetch = async (url, options = {}) => {
    const response = await fetch(url, {
      ...options,
      headers: { ...options.headers, Authorization: `Token ${token}` },
    });
    if (response.status === 401) await logout();
    return response;
  };

  return (
    <AuthContext.Provider value={{ token, profileId, isLoading, login, logout, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) throw new Error('useAuth must be used inside AuthProvider.');
  return context;
}
