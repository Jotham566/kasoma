import { randomUUID } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import type { components } from "@kasoma/api-client";
import { apiUrl } from "../../../config";

type Credentials = components["schemas"]["Credentials"];
const allowed: Record<string, string[]> = {
  "auth/otp/request": ["POST"],
  "auth/otp/verify": ["POST"],
  "auth/refresh": ["POST"],
  "auth/logout": ["POST"],
  "auth/logout-all": ["POST"],
  me: ["GET", "PATCH"],
  "me/consents": ["POST"],
  "curriculum/subjects": ["GET"],
};

async function gateway(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const path = (await context.params).path.join("/");
  const requestId = randomUUID();
  const fail = (status: number, code: string) =>
    NextResponse.json(
      {
        error: {
          code,
          message: "Please try again or sign in again.",
          request_id: requestId,
          field_errors: [],
        },
      },
      {
        status,
        headers: { "Cache-Control": "no-store", request_id: requestId },
      },
    );
  if (!allowed[path]?.includes(request.method))
    return fail(404, "RESOURCE_NOT_FOUND");
  if (
    request.method !== "GET" &&
    (request.headers.get("origin") !==
      `${request.nextUrl.protocol}//${request.headers.get("host")}` ||
      !["localhost", "127.0.0.1"].includes(
        new URL(request.headers.get("origin") ?? "http://invalid").hostname,
      ))
  ) {
    return fail(403, "FORBIDDEN");
  }
  try {
    let body: string | undefined;
    if (request.method !== "GET") {
      if (Number(request.headers.get("content-length") ?? 0) > 8192)
        return fail(413, "VALIDATION_FAILED");
      body = await request.text();
      if (body.length > 8192) return fail(413, "VALIDATION_FAILED");
    }
    if (path === "auth/refresh") {
      body = JSON.stringify({
        refresh_token: request.cookies.get("kasoma_refresh")?.value ?? "",
      });
    }
    const access = request.cookies.get("kasoma_access")?.value;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      request_id: requestId,
    };
    if (access) headers.Authorization = `Bearer ${access}`;
    const idempotency = request.headers.get("idempotency-key");
    if (idempotency) headers["Idempotency-Key"] = idempotency;
    const upstream = await fetch(`${apiUrl()}/api/v1/${path}`, {
      method: request.method,
      headers,
      body,
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    let response: NextResponse;
    const cookieOptions = {
      httpOnly: true,
      sameSite: "strict" as const,
      secure: request.nextUrl.protocol === "https:",
      path: "/",
    };
    if (upstream.ok && ["auth/otp/verify", "auth/refresh"].includes(path)) {
      const credentials: Credentials = await upstream.json();
      response = NextResponse.json({ authenticated: true });
      response.cookies.set("kasoma_access", credentials.access_token, {
        ...cookieOptions,
        maxAge: credentials.expires_in,
      });
      response.cookies.set("kasoma_refresh", credentials.refresh_token, {
        ...cookieOptions,
        maxAge: 30 * 86400,
      });
    } else {
      response = new NextResponse(
        upstream.status === 204 ? null : await upstream.text(),
        {
          status: upstream.status,
          headers: { "Content-Type": "application/json" },
        },
      );
      if (upstream.ok && path.startsWith("auth/logout")) {
        response.cookies.set("kasoma_access", "", {
          ...cookieOptions,
          maxAge: 0,
        });
        response.cookies.set("kasoma_refresh", "", {
          ...cookieOptions,
          maxAge: 0,
        });
      }
    }
    response.headers.set("Cache-Control", "no-store");
    response.headers.set("request_id", requestId);
    return response;
  } catch {
    return fail(503, "SERVICE_UNAVAILABLE");
  }
}
export { gateway as GET, gateway as POST, gateway as PATCH };
