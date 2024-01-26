import trafilatura

class SimpleScraper:
    """ trafilaturaを使ったシンプルなスクレイピング """

    def handle(self, url: str) -> tuple[str, str]:
        """ 指定したURLのページをスクレイピングしてテキストを返す """
        data = trafilatura.fetch_url(url)
        baseline = trafilatura.load_html(data)
        print(baseline.find("script"))
        # print(baseline.text_content())
        formatted_text = trafilatura.extract(data, include_formatting=True)
        not_formatted_text = trafilatura.extract(data, include_formatting=False)
        return not_formatted_text, formatted_text

if __name__ == "__main__":
    # python -m usecase.service.simple_scraper
    scraper = SimpleScraper()
    print(scraper.handle("https://chat.openai.com/share/8ae9e57e-4410-4757-936c-661e3fd80559"))
