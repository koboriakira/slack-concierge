from dataclasses import dataclass

@dataclass(frozen=True)
class PomodoroTimerRequest:
    page_id: str
    channel: str
    thread_ts: str
