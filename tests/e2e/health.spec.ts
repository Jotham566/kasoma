import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("health shell, keyboard retry and accessibility", async ({ page }) => {
  await page.route("**/*", (route) => {
    const host = new URL(route.request().url()).hostname;
    return ["127.0.0.1", "localhost"].includes(host)
      ? route.continue()
      : route.abort();
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Know what to revise next.",
  );
  await expect(page.getByRole("status")).toHaveText("Services are ready.");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Check again" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("status")).toHaveText("Services are ready.");
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
});
