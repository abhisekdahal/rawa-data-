from pathlib import Path
import json
import scrapy


class QProbeSpider(scrapy.Spider):
    name = "qprobe"
    custom_settings = {"ROBOTSTXT_OBEY": False}

    async def start(self):
        html_file = Path(__file__).resolve().parents[2] / "rawa.html"
        yield scrapy.Request(html_file.as_uri(), callback=self.parse, dont_filter=True)

    def parse(self, response):
        raw = response.css("div[data-page]::attr(data-page)").get()
        qp = json.loads(raw)["props"].get("quartsParticulars") or {}
        sample = {}
        for key in ["eps_ttm", "bvps", "net_profit_ttm", "revenue_ttm"]:
            val = qp.get(key)
            sample[key] = {
                "type": type(val).__name__,
                "length": len(val) if hasattr(val, "__len__") else None,
                "preview": json.dumps(val, ensure_ascii=False)[:400],
            }
        yield sample