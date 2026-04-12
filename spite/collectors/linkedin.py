import asyncio

from playwright.async_api import Page, async_playwright

from spite.collectors.base import BaseCollector, JobData
from spite.config import get_settings

settings = get_settings()

SESSION_DIR = ".browser_session"


class LinkedInCollector(BaseCollector):
    async def search(
        self, query: str, location: str = "", hours: int = 24
    ) -> list[JobData]:
        jobs: list[JobData] = []

        async with async_playwright() as p:
            browser_type = getattr(p, settings.browser)
            context = await browser_type.launch_persistent_context(
                SESSION_DIR,
                headless=self.headless,
                args=["--no-sandbox"],
            )

            page = await context.new_page()
            seconds = hours * 3600
            search_url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={query.replace(' ', '%20')}"
                f"&location={location.replace(' ', '%20')}"
                f"&f_TPR=r{seconds}"
            )

            await page.goto(search_url, wait_until="domcontentloaded")
            await asyncio.sleep(4)

            if await self._needs_login(page):
                print("⚠️  Login required. Please run the session setup first.")
                await context.close()
                return []

            jobs = await self._extract_jobs(page)
            await context.close()

        return jobs

    async def get_description(self, url: str) -> str | None:
        async with async_playwright() as p:
            browser_type = getattr(p, settings.browser)
            context = await browser_type.launch_persistent_context(
                SESSION_DIR,
                headless=self.headless,
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            description = None
            try:
                see_more = page.locator(".jobs-description__footer-button")
                if await see_more.count() > 0:
                    await see_more.click()
                    await asyncio.sleep(1)

                desc_el = page.locator(".jobs-description-content__text")
                if await desc_el.count() > 0:
                    description = await desc_el.inner_text()
            except Exception:
                pass

            await context.close()
            return description

    async def _needs_login(self, page: Page) -> bool:
        return "login" in page.url or "authwall" in page.url

    async def _extract_jobs(self, page: Page) -> list[JobData]:
        jobs = []

        try:
            await page.wait_for_selector(".job-card-list__entity-lockup", timeout=10000)
            cards = await page.query_selector_all(".scaffold-layout__list-item")

            for card in cards:
                try:
                    link_el = await card.query_selector("a.job-card-list__title--link")
                    if not link_el:
                        link_el = await card.query_selector("a[href*='/jobs/view/']")

                    company_el = await card.query_selector(
                        ".artdeco-entity-lockup__subtitle"
                    )
                    location_el = await card.query_selector(
                        ".job-card-container__metadata-wrapper"
                    )

                    title = await link_el.inner_text() if link_el else None
                    url = await link_el.get_attribute("href") if link_el else None
                    company = (
                        await company_el.inner_text() if company_el else "No company info"
                    )
                    location = await location_el.inner_text() if location_el else None

                    if not url or not title:
                        continue

                    if url.startswith("/"):
                        url = f"https://www.linkedin.com{url}"

                    url = url.split("?")[0]

                    jobs.append(
                        JobData(
                            title=title.strip(),
                            company=company.strip(),
                            url=url,
                            platform="linkedin",
                            location=location.strip() if location else None,
                        )
                    )

                except Exception:
                    continue

        except Exception as e:
            print(f"Error extracting jobs: {e}")

        return jobs
