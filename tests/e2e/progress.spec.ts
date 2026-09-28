import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("FR-MST-004/005: sparse progress, offline retry and sealed diagnostic history", async ({
  page,
}) => {
  await page.goto("/onboarding");
  await page
    .getByLabel("Email or mobile number", { exact: true })
    .fill("e6-progress@example.invalid");
  await page.getByRole("button", { name: "Send code", exact: true }).click();
  await page.getByLabel("Verification code", { exact: true }).fill("246810");
  await page.getByRole("button", { name: "Verify and continue" }).click();
  await page
    .getByLabel("Display name", { exact: true })
    .fill("Synthetic diagnostic learner");
  await page.getByLabel("Date of birth").fill("2000-01-01");
  await page.getByLabel("Mathematics", { exact: true }).check();
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(page.getByRole("status")).toHaveText("Profile saved.");
  await page
    .getByLabel("I give my own consent for this synthetic test.")
    .check();
  await page.getByRole("button", { name: "Record my consent" }).click();
  await expect(
    page.getByText("Required declarations are recorded.", { exact: false }),
  ).toBeVisible();
  await page.goto("/progress");
  await expect(page.getByRole("status")).toHaveText("Learning record loaded.");
  const overview = page.getByRole("region", { name: "Subject progress" });
  await expect(
    overview.getByText("Not enough evidence", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/Estimated mastery:/)).toHaveCount(0);
  await expect(overview.getByText("Evidence confidence: 0%.")).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.route(
    "**/api/v1/me/progress?*",
    (route) => route.abort("failed"),
    { times: 1 },
  );
  await page.getByRole("button", { name: "Reload learning record" }).click();
  await expect(page.getByRole("status")).toContainText(
    "Could not load your learning record",
  );
  await page.getByRole("button", { name: "Reload learning record" }).focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("status")).toHaveText("Learning record loaded.");
  await page.getByRole("link", { name: "History", exact: true }).click();
  await expect(page.getByText(/No sessions yet/)).toBeVisible();
  // Real owned cursor pagination through the web gateway, with unserved synthetic sessions.
  await page.evaluate(async () => {
    const profile = await (await fetch("/api/v1/me")).json();
    const subject = profile.subject_ids[0];
    const topics = await (
      await fetch(`/api/v1/curriculum/subjects/${subject}/topics`)
    ).json();
    for (let i = 0; i < 11; i++) {
      const response = await fetch("/api/v1/revision-sessions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": crypto.randomUUID(),
        },
        body: JSON.stringify({
          subject_id: subject,
          topic_id: topics[0].id,
          mode: "TOPIC",
          desired_item_count: 5,
          channel: "WEB",
        }),
      });
      if (response.status !== 201)
        throw new Error("Synthetic history setup failed");
      const session = await response.json();
      const abandoned = await fetch(`/api/v1/sessions/${session.id}/abandon`, {
        method: "POST",
      });
      if (!abandoned.ok) throw new Error("Synthetic abandonment failed");
    }
  });
  await page.getByRole("button", { name: "Reload learning record" }).click();
  const history = page.getByRole("region", { name: "Session history" });
  await expect(history.getByRole("article")).toHaveCount(10);
  await page.getByRole("button", { name: "Load older sessions" }).focus();
  await page.keyboard.press("Enter");
  await expect(history.getByRole("article")).toHaveCount(11);
  await expect(
    page.getByRole("button", { name: "Load older sessions" }),
  ).toHaveCount(0);
  await page.goto("/diagnostic");
  await page
    .getByRole("button", { name: "Start or resume diagnostic" })
    .click();
  await page.getByRole("radio", { name: "Alpha", exact: true }).check();
  await page.getByRole("button", { name: "Save answer and continue" }).click();
  await expect(
    page.getByText("1 of 15 answers saved", { exact: true }),
  ).toBeVisible();
  await page.goto("/progress");
  await expect(overview.getByText("Evidence confidence: 0%.")).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Continue your diagnostic" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "History", exact: true }).click();
  await expect(
    page.getByText("Status: active. 1 of 15 answers saved."),
  ).toBeVisible();
  await expect(
    page.getByText(/Estimated mastery:|points awarded/i),
  ).toHaveCount(0);
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await page.getByRole("link", { name: "Resume session" }).click();
  await expect(
    page.getByRole("group", { name: "Question 2", exact: true }),
  ).toBeVisible();
});
