import trafilatura

class SimpleScraper:
    """ trafilaturaを使ったシンプルなスクレイピング """

    def handle(self, url: str) -> str:
        """ 指定したURLのページをスクレイピングしてテキストを返す """
        data = trafilatura.fetch_url(url)
        return trafilatura.extract(data)
