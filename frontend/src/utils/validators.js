// simple, well-documented validators used by the signup form

export function validateEmail(email) {
  if (!email || typeof email !== "string") return false;
  const normalized = email.trim();
  // RFC-like but pragmatic regex for common emails
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
  return re.test(normalized);
}

/**
 * validatePassword returns an object of booleans for each rule
 */
export function validatePassword(password = "") {
  const res = {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    symbol: /[!@#$%^&*(),.?":{}|<>_\-\\[\];'`~+=/]/.test(password),
  };
  return res;
}

export const passwordRequirementsText = {
  length: "At least 8 characters",
  upper: "At least one uppercase letter (A–Z)",
  lower: "At least one lowercase letter (a–z)",
  number: "At least one number (0–9)",
  symbol: "At least one symbol (e.g. !@#$%)",
};