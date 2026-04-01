import { API_URL } from "@/lib/constants";

export async function fetchMe() {
  const res = await fetch(`${API_URL}/auth/me`, {
    credentials: "include",
  });
  if (!res.ok) return null;
  return res.json();
}

export async function loginWithGoogle() {
  const res = await fetch(`${API_URL}/auth/google`, {
    credentials: "include",
  });
  const data = await res.json();
  return data.url as string;
}

export async function loginWithGithub() {
  const res = await fetch(`${API_URL}/auth/github`, {
    credentials: "include",
  });
  const data = await res.json();
  return data.url as string;
}

export async function logout() {
  await fetch(`${API_URL}/auth/logout`, {
    credentials: "include",
  });
}
