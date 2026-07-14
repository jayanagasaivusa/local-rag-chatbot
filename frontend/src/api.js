// Thin wrapper around the FastAPI backend, built on a shared axios instance.
// A request interceptor attaches the JWT (from localStorage) to every call,
// and a response interceptor logs the user out on 401s.
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const TOKEN_STORAGE_KEY = 'rag_access_token';

export const apiClient = axios.create({ baseURL: API_BASE_URL });

export function getStoredToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Registered by AuthContext so a 401 anywhere can trigger a clean logout
// (clears the stored token + redirects to /login) without every call site
// needing to know about auth.
let onUnauthorized = () => {};
export function registerUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      onUnauthorized();
    }
    return Promise.reject(error);
  },
);

function extractErrorMessage(error) {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return error.message || 'Something went wrong.';
}

// --- Auth --------------------------------------------------------------

export async function registerUser(email, password) {
  try {
    const { data } = await apiClient.post('/register', { email, password });
    return data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

export async function loginUser(email, password) {
  try {
    const { data } = await apiClient.post('/login', { email, password });
    return data; // { access_token, token_type }
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

// --- Chat sessions -------------------------------------------------------

export async function listSessions() {
  try {
    const { data } = await apiClient.get('/sessions');
    return data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

export async function getSessionMessages(sessionId) {
  try {
    const { data } = await apiClient.get(`/sessions/${sessionId}/messages`);
    return data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

export async function deleteSession(sessionId) {
  try {
    await apiClient.delete(`/sessions/${sessionId}`);
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

// --- Documents / chat ----------------------------------------------------

/**
 * Uploads a single file to the /upload endpoint for ingestion into Chroma.
 * @param {File} file
 * @returns {Promise<{filename: string, chunks_added: number, message: string}>}
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const { data } = await apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

/**
 * Sends a chat message to the /chat endpoint and returns the AI response.
 * @param {string} message
 * @param {string|null} sessionId
 * @returns {Promise<{response: string, sources: string[], session_id: string}>}
 */
export async function sendChatMessage(message, sessionId) {
  try {
    const { data } = await apiClient.post('/chat', { message, session_id: sessionId });
    return data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

/**
 * Fetches the list of documents currently ingested into the vector store.
 * @returns {Promise<{documents: string[]}>}
 */
export async function listDocuments() {
  try {
    const { data } = await apiClient.get('/documents');
    return data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

export { API_BASE_URL };
