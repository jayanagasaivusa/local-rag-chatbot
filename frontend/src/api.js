// Thin wrapper around the FastAPI backend. Keeping all fetch/error-handling
// logic here means the components never need to know about URLs or response
// shapes directly.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function parseErrorMessage(response) {
  try {
    const data = await response.json();
    return data.detail || data.message || `Request failed (${response.status})`;
  } catch {
    return `Request failed (${response.status})`;
  }
}

/**
 * Uploads a single file to the /upload endpoint for ingestion into Chroma.
 * @param {File} file
 * @returns {Promise<{filename: string, chunks_added: number, message: string}>}
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  return response.json();
}

/**
 * Sends a chat message to the /chat endpoint and returns the AI response.
 * @param {string} message
 * @returns {Promise<{response: string, sources: Array<{source: string, snippet: string}>}>}
 */
export async function sendChatMessage(message) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  return response.json();
}

/**
 * Fetches the list of documents currently ingested into the vector store.
 * @returns {Promise<{documents: string[]}>}
 */
export async function listDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`);
  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }
  return response.json();
}

export { API_BASE_URL };
