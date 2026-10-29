export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail ?? data?.error ?? data?.message;
    throw new Error(typeof detail === 'string' ? detail : detail ? JSON.stringify(detail) : `Request failed (${response.status}).`);
  }
  return data as T;
}

export const jsonBody = (value: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(value) });
