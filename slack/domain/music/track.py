from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Track:
    track_id: str
    track_name: str
    artists: list[str]
    cover_url: str|None = None
    release_date: date|None = None
    spotify_url: str|None = None

    @staticmethod
    def from_spotify_track_info(track_info:dict) -> "Track":
        return Track(
            track_id=track_info["id"],
            track_name=track_info["name"],
            artists=track_info["artists"],
            cover_url=track_info["cover_url"],
            release_date=date.fromisoformat(track_info["release_date"]) if track_info["release_date"] else None,
            spotify_url=track_info["spotify_url"],
        )

    def to_dict(self) -> dict:
        data = {
            "track_name": self.track_name,
            "artists": self.artists,
        }
        if self.spotify_url:
            data["spotify_url"] = self.spotify_url
        if self.cover_url:
            data["cover_url"] = self.cover_url
        if self.release_date:
            data["release_date"] = self.release_date.strftime("%Y-%m-%d")
        return data
