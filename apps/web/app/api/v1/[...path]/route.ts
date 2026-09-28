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
  "me/recommendations/next": ["GET"],
  "me/progress": ["GET"],
  "me/session-history": ["GET"],
  "curriculum/subjects": ["GET"],
  "revision-sessions": ["POST"],
  diagnostics: ["POST"],
  "sessions/active": ["GET"],
  "admin/content-context": ["GET"],
  "admin/items": ["GET", "POST"],
  "admin/content-flags": ["GET"],
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
  const staffVersion =
    /^admin\/item-versions\/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(?:\/(submit|review|retire|reviews))?$/.exec(
      path,
    );
  const uuid =
    "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
  const learning = new RegExp(
    `^sessions/${uuid}(?:/(next-item|attempts|abandon))?$`,
  ).exec(path);
  const learningRead = new RegExp(
    `^(?:diagnostics/${uuid}|attempts/${uuid}/(?:grade|solution|hints)|curriculum/subjects/${uuid}/topics)$`,
  ).test(path);
  const hintWrite = new RegExp(
    `^(?:sessions/${uuid}/items/${uuid}/hint|attempts/${uuid}/hint)$`,
  ).test(path);
  const reassessment = new RegExp(`^attempts/${uuid}/reassessment$`).test(path);
  const flagReport = new RegExp(`^attempts/${uuid}/flag$`).test(path);
  const flagTriage = new RegExp(`^admin/content-flags/${uuid}$`).test(path);
  const methods = flagReport
    ? ["GET", "POST"]
    : flagTriage
      ? ["GET", "PATCH"]
      : reassessment
        ? ["GET", "POST"]
        : hintWrite
          ? ["POST"]
          : learning
            ? [
                learning[1] === "attempts" || learning[1] === "abandon"
                  ? "POST"
                  : "GET",
              ]
            : learningRead
              ? ["GET"]
              : staffVersion
                ? staffVersion[1] === "reviews"
                  ? ["GET"]
                  : staffVersion[1]
                    ? ["POST"]
                    : ["GET", "PATCH"]
                : allowed[path];
  if (!methods?.includes(request.method))
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
      if (Number(request.headers.get("content-length") ?? 0) > 65536)
        return fail(413, "VALIDATION_FAILED");
      body = await request.text();
      if (new TextEncoder().encode(body).length > 65536)
        return fail(413, "VALIDATION_FAILED");
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
    const query = new URLSearchParams();
    if (path === "admin/content-flags") {
      const status = request.nextUrl.searchParams.get("status");
      if (status) query.set("status", status);
    }
    if (
      ["admin/items", "admin/content-flags", "me/session-history"].includes(
        path,
      )
    )
      for (const key of ["cursor", "limit"]) {
        const value = request.nextUrl.searchParams.get(key);
        if (value !== null) query.set(key, value);
      }
    if (
      ["me/recommendations/next", "me/progress", "me/session-history"].includes(
        path,
      )
    ) {
      const subject = request.nextUrl.searchParams.get("subject_id");
      if (subject !== null) query.set("subject_id", subject);
    }
    const upstream = await fetch(`${apiUrl()}/api/v1/${path}?${query}`, {
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
