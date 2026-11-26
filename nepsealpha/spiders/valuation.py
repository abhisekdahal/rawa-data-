from pathlib import Path
import json
import scrapy


class ValuationSpider(scrapy.Spider):
    name = "valuation"
    custom_settings = {"ROBOTSTXT_OBEY": False}

    async def start(self):
        project_dir = Path(__file__).resolve().parents[2]
        for html_file in sorted(project_dir.glob("*.html")):
            yield scrapy.Request(
                html_file.as_uri(),
                callback=self.parse,
                dont_filter=True,
                cb_kwargs={"file_name": html_file.name},
            )

    def parse(self, response, file_name):
        raw = response.css("div[data-page]::attr(data-page)").get()
        if not raw:
            self.logger.warning("No data-page found in %s, skipping", file_name)
            return
        props = json.loads(raw)["props"]
        symbol = props.get("symbol")

        for row in props.get("otherQuartGrowths") or []:
            yield {
                "symbol": symbol,
                "date": row.get("date"),
                "pe_ratio": row.get("pe_ratio"),
                "pb_ratio": row.get("pb_ratio"),
                "price_to_sales": row.get("ps"),
                "source_file": file_name,
            }