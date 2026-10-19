import type { components } from "@kasoma/api-client";

export type Key = keyof components["schemas"]["WarningValues"];
export const settings: Record<
  Key,
  { label: string; min: number; max: number; unit: string }
> = {
  request_p95_ms: {
    label: "API response-start p95",
    min: 1,
    max: 60000,
    unit: "milliseconds",
  },
  request_min_samples: {
    label: "API timing minimum sample",
    min: 1,
    max: 10000,
    unit: "requests",
  },
  failed_imports: {
    label: "Failed imports in 24 hours",
    min: 1,
    max: 10000,
    unit: "imports",
  },
  import_age_seconds: {
    label: "Oldest pending import",
    min: 60,
    max: 86400,
    unit: "seconds",
  },
  unresolved_flags: {
    label: "Unresolved content flags",
    min: 1,
    max: 10000,
    unit: "flags",
  },
  channel_failures: {
    label: "Channel failures in 24 hours",
    min: 1,
    max: 10000,
    unit: "messages",
  },
  channel_queue_age_seconds: {
    label: "Oldest pending channel message",
    min: 1,
    max: 86400,
    unit: "seconds",
  },
  channel_dispatch_p95_ms: {
    label: "Local channel dispatch p95",
    min: 1,
    max: 60000,
    unit: "milliseconds",
  },
  channel_dispatch_min_samples: {
    label: "Channel timing minimum sample",
    min: 1,
    max: 1000,
    unit: "messages",
  },
  otp_failures: {
    label: "Observed OTP adapter failures",
    min: 1,
    max: 10000,
    unit: "failures",
  },
  model_gateway_attempts: {
    label: "Observed local model attempts",
    min: 1,
    max: 10000,
    unit: "attempts",
  },
  grading_age_seconds: {
    label: "Oldest pending grading work",
    min: 1,
    max: 86400,
    unit: "seconds",
  },
  export_failures: {
    label: "Failed personal exports in 24 hours",
    min: 1,
    max: 10000,
    unit: "exports",
  },
  export_age_seconds: {
    label: "Oldest pending personal export",
    min: 60,
    max: 86400,
    unit: "seconds",
  },
  retirement_stall_seconds: {
    label: "Synthetic maintenance heartbeat age",
    min: 120,
    max: 7200,
    unit: "seconds",
  },
};
