export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export async function getApiJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.error || `Erreur API (${response.status})`);
  }
  return response.json();
}
