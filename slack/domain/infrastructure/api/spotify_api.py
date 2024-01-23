from abc import ABCMeta, abstractmethod

class SpotifyApi(metaclass=ABCMeta):
    @abstractmethod
    def love_track(self) -> bool:
        """ Spotifyのトラックを「お気に入りの曲」ライブラリに追加する """
        pass

    @abstractmethod
    def find_track(self, track_id: str) -> dict:
        """ Spotifyのトラックの情報を取得する """
