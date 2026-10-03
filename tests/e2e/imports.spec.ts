import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-CNT-001: synthetic file import survives lost acknowledgement and opens a draft", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e2e-content-import-author@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await expect(page.getByLabel("Display name", { exact: true })).toBeVisible();
  await page.goto("/admin/content/imports");
  await page.getByLabel("Draft JSON file").setInputFiles({
    name: "invalid.json",
    mimeType: "application/json",
    buffer: Buffer.from("not json"),
  });
  await page.getByRole("button", { name: "Queue draft import" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "The file is not valid JSON.",
  );
  const subject = await page.evaluate(async () => {
    const response = await fetch("/api/v1/admin/content-context");
    return (await response.json()).subjects[0].id as string;
  });
  const body = {
    format_version: "kasoma-draft-import-v1",
    synthetic: true,
    records: [
      {
        subject_id: subject,
        change_reason: "Browser synthetic import",
        document: {
          title: "Imported browser fixture",
          source: "Original synthetic browser item",
          source_locator: "browser:1",
          rights_status: "ORIGINAL_KASOMA",
          rights_evidence: "Original fixture without third-party material",
        },
      },
    ],
  };
  await page.getByLabel("Draft JSON file").setInputFiles({
    name: "drafts.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(body)),
  });
  let dropped = false;
  await page.route("**/api/v1/admin/content-imports", async (route) => {
    if (route.request().method() === "POST" && !dropped) {
      dropped = true;
      await route.fetch();
      await route.abort("failed");
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Queue draft import" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Connection interrupted. Retry with the same file.",
  );
  await page.getByRole("button", { name: "Queue draft import" }).click();
  await expect(page.getByRole("status")).toContainText("Import accepted.");
  await expect(async () => {
    await page.getByRole("button", { name: "Refresh import status" }).click();
    await expect(
      page.getByRole("link", { name: "Record 1: Open draft" }),
    ).toHaveCount(1);
  }).toPass();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByRole("link", { name: "Record 1: Open draft" }).click();
  await expect(page.getByLabel("Title", { exact: true })).toHaveValue(
    "Imported browser fixture",
  );
  await expect(
    page.getByRole("textbox", { name: "Source locator", exact: true }),
  ).toHaveValue("browser:1");
  await expect(
    page.getByRole("button", { name: "Save draft", exact: true }),
  ).toBeVisible();
});
