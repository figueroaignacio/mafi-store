"""
LinkedIn collector.
Scrapeamos LinkedIn porque la vida es demasiado corta para hacerlo a mano.
"""
import asyncio
from playwright.async_api import async_playwright, Page
from spite.collectors.base import BaseCollector, JobData
from spite.config import get_settings

settings = get_settings()

SESSION_DIR = ".browser_session"


class LinkedInCollector(BaseCollector):

    async def search(
        self, query: str, location: str = "", hours: int = 24, max_jobs: int = 50
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
                print("⚠️  Need to login first. Run the session setup.")
                await context.close()
                return []

            await self._scroll_to_load(page, max_jobs)
            jobs = await self._extract_jobs(page, max_jobs)
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

    async def _scroll_to_load(self, page: Page, max_jobs: int) -> None:
        """
        Scroll the page until we have enough jobs or nothing new loads.
        Uses the scaffold list container — the correct selector for LinkedIn's current layout.
        """
        previous_count = 0
        no_change_attempts = 0

        while True:
            cards = await page.query_selector_all(".scaffold-layout__list-item")
            current_count = len(cards)

            print(f"  Cards loaded: {current_count}")

            if current_count >= max_jobs:
                break

            if current_count == previous_count:
                no_change_attempts += 1
                if no_change_attempts >= 3:
                    break
            else:
                no_change_attempts = 0

            previous_count = current_count

            # Scroll dentro del contenedor correcto
            await page.evaluate("""
                const list = document.querySelector('.scaffold-layout__list');
                if (list) list.scrollTo(0, list.scrollHeight);
                else window.scrollTo(0, document.body.scrollHeight);
            """)
            await asyncio.sleep(2)

            # Botón "ver más" si aparece
            see_more = page.locator("button.infinite-scroller__show-more-button")
            if await see_more.count() > 0:
                await see_more.click()
                await asyncio.sleep(2)

    async def _extract_jobs(self, page: Page, max_jobs: int = 50) -> list[JobData]:
        jobs = []

        try:
            cards = await page.query_selector_all(".scaffold-layout__list-item")

            for card in cards[:max_jobs]:
                try:
                    link_el = await card.query_selector("a.job-card-list__title--link")
                    if not link_el:
                        link_el = await card.query_selector("a[href*='/jobs/view/']")

                    company_el = await card.query_selector(".artdeco-entity-lockup__subtitle")
                    location_el = await card.query_selector(".job-card-container__metadata-wrapper")

                    title = await link_el.inner_text() if link_el else None
                    url = await link_el.get_attribute("href") if link_el else None
                    company = await company_el.inner_text() if company_el else "Unknown"
                    location = await location_el.inner_text() if location_el else None

                    if not url or not title:
                        continue

                    if url.startswith("/"):
                        url = f"https://www.linkedin.com{url}"

                    url = url.split("?")[0]

                    jobs.append(JobData(
                        title=title.strip(),
                        company=company.strip(),
                        url=url,
                        platform="linkedin",
                        location=location.strip() if location else None,
                    ))

                except Exception:
                    continue

        except Exception as e:
            print(f"Error extracting jobs: {e}")

        return jobs
