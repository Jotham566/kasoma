import createClient from "openapi-fetch";
import type { paths } from "./schema";

export function apiClient(baseUrl: string, requestId: string) {
  return createClient<paths>({ baseUrl, headers: { request_id: requestId } });
}
