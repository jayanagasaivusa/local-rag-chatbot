import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { jwtDecode } from 'jwt-decode';
import {
  getStoredToken,
  loginUser,
  registerUnauthorizedHandler,
  registerUser,
  setStoredToken,
} from '../api';

const AuthContext = createContext(null);

function decodeUser(token) {
  if (!token) return null;
  try {
    const payload = jwtDecode(token);
    // Reject already-expired tokens (e.g. left over from a previous session).
    if (payload.exp && payload.exp * 1000 < Date.now()) return null;
    return { id: payload.sub };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getStoredToken());
  const [user, setUser] = useState(() => decodeUser(getStoredToken()));

  const logout = useCallback(() => {
    setStoredToken(null);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    registerUnauthorizedHandler(logout);
  }, [logout]);

  const login = useCallback(async (email, password) => {
    const { access_token } = await loginUser(email, password);
    setStoredToken(access_token);
    setToken(access_token);
    setUser(decodeUser(access_token));
  }, []);

  const register = useCallback(async (email, password) => {
    await registerUser(email, password);
    // Auto-login right after a successful registration for a smoother UX.
    await login(email, password);
  }, [login]);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      login,
      register,
      logout,
    }),
    [token, user, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
