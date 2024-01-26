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
    print(scraper.handle("https://youtube.com/watch?v=_PNyMj6hQeM&amp;si=9zQ3VM2TE1aLeCxH"))
