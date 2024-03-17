from dataclasses import dataclass

from domain.channel.channel_type import ChannelType


@dataclass(frozen = True)
class Thread:
    channel_id: str | None
    event_ts: str | None
    thread_ts: str | None

    @staticmethod
    def create(
        channel_id: ChannelType|str|None = None,
        event_ts: str|None = None,
        thread_ts:str|None = None) -> "Thread":
        return Thread(
          channel_id = _get_channel_id(channel_id),
          event_ts = event_ts or thread_ts,
          thread_ts = thread_ts or event_ts,
        )

    @staticmethod
    def empty() -> "Thread":
        return Thread.create(
            channel_id = None,
            event_ts = None,
            thread_ts = None,
        )

def _get_channel_id(channel: ChannelType|str|None) -> str:
    if channel is None:
        return ChannelType.BOT_DM.value
    return channel if isinstance(channel, str) else channel.value
