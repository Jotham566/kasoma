/** Closed messages only: query parameters never become reflected provider diagnostics. */
const messages = {
  REAUTH_REQUIRED:
    "Sign in again to verify your identity before downloading your export.",
  FORBIDDEN:
    "This export is not available to this account. Sign in again or reload your requests.",
  RESOURCE_NOT_FOUND: "This export could not be found. Reload your requests.",
  EXPORT_NOT_READY:
    "Your export is not ready. Check its status before downloading again.",
  EXPORT_EXPIRED: "This copy has expired. Submit a new export request.",
  RATE_LIMITED: "Too many download requests. Wait before trying again.",
  SERVICE_UNAVAILABLE:
    "The download could not start. Check your connection and try again. Your request is retained.",
} as const;

export function exportNotice(code: unknown): string | undefined {
  return typeof code === "string" && Object.hasOwn(messages, code)
    ? messages[code as keyof typeof messages]
    : undefined;
}

export function exportFailureLocation(code: string): string {
  const safeCode = exportNotice(code) ? code : "SERVICE_UNAVAILABLE";
  return `/privacy?export_error=${safeCode}`;
}
