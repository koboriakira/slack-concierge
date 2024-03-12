from dataclasses import dataclass


@dataclass(frozen = True)
class Thread:
    channel_id: str
    event_ts: str | None
    thread_ts: str | None

    @staticmethod
    def create(channel_id: str, event_ts: str|None = None, thread_ts:str|None = None) -> "Thread":
        return Thread(
          channel_id = channel_id,
          event_ts = event_ts or thread_ts,
          thread_ts = thread_ts or event_ts,
        )
