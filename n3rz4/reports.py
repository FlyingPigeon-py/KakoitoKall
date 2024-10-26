from telethon import TelegramClient
from re import compile as compile_link
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonSpam
from os import listdir

path: str = "n3rz4/sessions/"


async def count_session(api_id, api_hash, botm) -> None:
    files = listdir(path)
    sessions = [s for s in files if s.endswith(".session")]
    count = 0
    for session in sessions:
        client: TelegramClient = TelegramClient(
            "n3rz4/sessions/{}".format(session), api_id, api_hash
        )
        await client.connect()

        if not client.is_user_authorized:
            print("Сессия {} не авторизована.".format(session))
        else:
            count += 1
            await botm.edit(
                f"🔄 <b>Количество найденных сессий</b>: {count}",
                parse_mode="html",
            )
        await client.disconnect()
    return count


async def report_message(link, api_id, api_hash) -> None:
    message_link_pattern = compile_link(
        r"https://t.me/(?P<username_or_chat>.+)/(?P<message_id>\d+)"
    )
    match = message_link_pattern.search(link)
    if match:
        chat = match.group("username_or_chat")
        message_id = int(match.group("message_id"))
        files = listdir(path)
        sessions = [s for s in files if s.endswith(".session")]
        for session in sessions:
            client: TelegramClient = TelegramClient(
                "n3rz4/sessions/{}".format(session), api_id, api_hash
            )
            await client.connect()

            if not client.is_user_authorized:
                print("Сессия {} не авторизована.".format(session))

            print(123)

            try:
                entity = await client.get_entity(chat)
                await client(
                    ReportRequest(
                        peer=entity,
                        id=[message_id],
                        reason=InputReportReasonSpam(),
                        message="В этом сообщении наблюдается спам.",
                    )
                )

                print("Жалоба отправлена.")

                await client.disconnect()

            except Exception as e:
                await client.disconnect()
                print(e)
