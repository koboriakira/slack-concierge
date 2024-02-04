from dataclasses import dataclass

@dataclass(frozen=True)
class PomodoroTimerRequest:
    page_id: str
    channel: str
    thread_ts: str

    @staticmethod
    def from_event(event: dict) -> "PomodoroTimerRequest":
        return PomodoroTimerRequest(
            page_id=event["page_id"],
            channel=event["channel"],
            thread_ts=event["thread_ts"],
        )
