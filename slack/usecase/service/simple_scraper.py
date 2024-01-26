import trafilatura

class SimpleScraper:
    """ trafilaturaを使ったシンプルなスクレイピング """

    def handle(self, url: str) -> tuple[str, str]:
        """ 指定したURLのページをスクレイピングしてテキストを返す """
        data = trafilatura.fetch_url(url)
        formatted_text = trafilatura.extract(data, include_formatting=True)
        not_formatted_text = trafilatura.extract(data, include_formatting=False)
        return not_formatted_text, formatted_text

if __name__ == "__main__":
    # python -m usecase.service.simple_scraper
    scraper = SimpleScraper()
    print(scraper.handle("https://qiita.com/kobori_akira/items/8f721c17b9340d7f4219"))
