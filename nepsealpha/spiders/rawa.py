from pathlib import Path
import json
import scrapy


class RawaSpider(scrapy.Spider):
    name = "rawa"
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
        if not props.get("latestPrice"):
            self.logger.warning("No price data in %s, skipping", file_name)
            return

        price = props.get("latestPrice") or {}
        master = props.get("masterData") or {}
        funda = props.get("funda_table") or {}
        general = props.get("stocksGenralInfo") or {}
        stock = props.get("stock_info") or {}

        def pct(x):
            return round(x * 100, 2) if isinstance(x, (int, float)) else None

        def rnd(x, n=2):
            return round(x, n) if isinstance(x, (int, float)) else None

        yield {
            "symbol": props.get("symbol"),
            "company": stock.get("full_name"),
            "sector": stock.get("sector"),
            "ltp": price.get("today_price"),
            "percent_change": rnd(price.get("percent_change")),
            "open": price.get("open"),
            "high": price.get("high"),
            "low": price.get("low"),
            "previous_close": price.get("previous_close"),
            "volume": price.get("volume"),
            "turnover": rnd(price.get("turn_over")),
            "as_of_utc": price.get("updated_at"),
            "week_52_high": master.get("_52_weeks_hi"),
            "week_52_low": master.get("_52_weeks_lo"),
            "eps": rnd(master.get("eps")),
            "book_value": rnd(master.get("book_value")),
            "shares_outstanding": master.get("shares_outstnading"),
            "pe_ratio": rnd(funda.get("pe_ratio")),
            "pb_ratio": rnd(funda.get("pb_ratio")),
            "roe_percent": pct(funda.get("roe")),
            "roa_percent": pct(funda.get("roa")),
            "graham_number": rnd(funda.get("graham_number")),
            "listed_date": general.get("listed_date"),
            "installed_capacity": general.get("installed_capacity"),
            "operation_date": general.get("operation_date"),
            "per_mega_watt_cost": general.get("per_mega_watt_cost"),
            "normal_pay_back": general.get("normal_pay_back"),
            "source_file": file_name,
        }