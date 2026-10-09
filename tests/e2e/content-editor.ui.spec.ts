import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import type { components } from "@kasoma/api-client";

type Version = components["schemas"]["VersionView"];
const id = (n: number) =>
  `00000000-0000-4000-8000-${String(n).padStart(12, "0")}`;

test("FR-CNT-003: controlled rubric survives save and explicit reload", async ({
  page,
}) => {
  const context: components["schemas"]["ContentContext"] = {
    actor_id: id(1),
    roles: ["CONTENT_AUTHOR"],
    subjects: [{ id: id(2), name: "Mathematics" }],
    topics: [{ id: id(3), parent_id: id(2), name: "Synthetic topic" }],
    concepts: [
      {
        id: id(4),
        parent_id: id(3),
        name: "Synthetic concept",
        syllabus_reference: "synthetic",
      },
    ],
    competencies: [{ id: id(5), name: "Synthetic competency" }],
    checklist: [],
  };
  let stored: Version | null = null;
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    if (path.endsWith("/content-context"))
      return route.fulfill({ json: context });
    if (path.endsWith("/reviews")) return route.fulfill({ json: [] });
    if (path.endsWith("/items") && request.method() === "GET")
      return route.fulfill({ json: { data: [], next_cursor: null } });
    if (path.endsWith("/items") && request.method() === "POST") {
      const body =
        request.postDataJSON() as components["schemas"]["CreateDraft"];
      expect(body.document.response_type).toBe("SHORT_TEXT");
      expect(body.document.rubric?.criteria[0].acceptable_evidence).toEqual([
        "Alpha\non its own line",
      ]);
      stored = {
        id: id(6),
        item_id: id(7),
        subject_id: id(2),
        author_id: id(1),
        version: 1,
        revision: 1,
        status: "DRAFT",
        document: body.document,
        rubric_version_id: id(6),
        requires_second_review: false,
        approval_count: 0,
        created_at: "2026-10-09T00:00:00Z",
        updated_at: "2026-10-09T00:00:00Z",
      };
      return route.fulfill({ status: 201, json: stored });
    }
    if (path.endsWith(`/item-versions/${id(6)}`))
      return route.fulfill({ json: stored });
    throw new Error("Unexpected synthetic UI request");
  });
  await page.goto("/admin/content");
  await expect(page.getByRole("status")).toHaveText("Staff workspace ready.");
  await page.getByLabel("Response format").selectOption("SHORT_TEXT");
  await page
    .getByRole("button", { name: "Add criterion", exact: true })
    .click();
  await page.getByLabel("Criterion text", { exact: true }).fill("Write Alpha.");
  await page
    .getByLabel("Acceptable evidence 1", { exact: true })
    .fill("Alpha\non its own line");
  await page
    .getByLabel("Change reason", { exact: true })
    .fill("Synthetic rubric save");
  await page.screenshot({
    path: ".local/ui-review/content-editor-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 320, height: 740 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.screenshot({
    path: ".local/ui-review/content-editor-mobile.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Save draft", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Version 1: DRAFT.");
  await expect(page.getByLabel("Response format")).toHaveValue("SHORT_TEXT");
  await expect(
    page.getByLabel("Acceptable evidence 1", { exact: true }),
  ).toHaveValue("Alpha\non its own line");
  await page.getByRole("button", { name: "Reload selected item" }).click();
  await expect(page.getByRole("status")).toHaveText("Version 1: DRAFT.");
  await expect(
    page.getByLabel("Acceptable evidence 1", { exact: true }),
  ).toHaveValue("Alpha\non its own line");
});
