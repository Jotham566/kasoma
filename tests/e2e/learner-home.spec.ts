import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

for (const width of [320, 1280]) {
  test(`NFR-ACC-001/NFR-COMP-001: learner home and navigation at ${width}px`, async ({
    page,
  }, testInfo) => {
    await page.setViewportSize({ width, height: 900 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    const navigation = page.getByRole("navigation", {
      name: "Learner navigation",
      exact: true,
    });
    await expect(navigation).toHaveCount(1);
    await expect(
      navigation.getByRole("link", { name: "Home", exact: true }),
    ).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("main")).toHaveCount(1);
    await expect(
      page
        .getByRole("region", { name: "Recommended practice" })
        .getByRole("status"),
    ).toHaveText("Sign in to see your next activity.");
    await expect(
      page.getByText(
        "Synthetic practice only. Academic approval remains pending.",
      ),
    ).toBeVisible();
    const reflow = async () => {
      expect(
        await page.evaluate(() =>
          Math.max(
            document.body.scrollWidth,
            document.documentElement.scrollWidth,
          ),
        ),
      ).toBeLessThanOrEqual(width);
    };
    await reflow();
    for (const link of await navigation.getByRole("link").all()) {
      const bounds = await link.boundingBox();
      expect(bounds!.width).toBeGreaterThanOrEqual(44);
      expect(bounds!.height).toBeGreaterThanOrEqual(44);
    }
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: testInfo.outputPath(`learner-home-${width}.png`),
      fullPage: true,
    });
    // Enlarged text must still leave every navigation destination reachable.
    await page.evaluate(() => {
      document.documentElement.style.fontSize = "200%";
    });
    await reflow();
    const profile = navigation.getByRole("link", {
      name: "Profile & settings",
      exact: true,
    });
    await profile.focus();
    await expect(profile).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/\/onboarding$/);
    await expect(
      navigation.getByRole("link", { name: "Profile & settings", exact: true }),
    ).toHaveAttribute("aria-current", "page");
    await expect(
      page.getByLabel("Email or mobile number", { exact: true }),
    ).toBeVisible();
    await reflow();
    await expect(
      page.getByRole("link", { name: "Find your starting point", exact: true }),
    ).toHaveCount(0);
    await page.evaluate(() => {
      document.documentElement.style.fontSize = "100%";
    });
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    await page.screenshot({
      path: testInfo.outputPath(`onboarding-${width}.png`),
      fullPage: true,
    });
    await page.goto("/admin/operations");
    await expect(navigation).toHaveCount(0);
    await page.getByRole("button", { name: "Refresh operations" }).click();
    await expect(page.getByRole("status")).toContainText(
      "Snapshot unavailable.",
    );
  });
}
