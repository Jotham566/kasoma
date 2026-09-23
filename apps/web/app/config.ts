import "server-only";
import { z } from "zod";

export function apiUrl() {
  return z
    .url()
    .refine(
      (value) =>
        ["localhost", "127.0.0.1", "api"].includes(new URL(value).hostname),
      "Local API required",
    )
    .parse(process.env.API_INTERNAL_URL ?? "http://localhost:8000");
}
