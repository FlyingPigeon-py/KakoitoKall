from telethon import TelegramClient, events
from n3rz4.functions import TelegramBot


class DrozloerBot:
    def __init__(self) -> None:
        # Initialize API credentials and client
        self.api_id: int = 27222922
        self.api_hash: str = "c4a6bf3f63dc8d8b272376a3d004efd8"
        self.token: str = "7051864962:AAF293DTYcSG-Tedtxs8yD07PlOxFUGz8bM"
        self.client: TelegramClient = TelegramClient(
            "__main__", self.api_id, self.api_hash
        )

        self.client.start(bot_token=self.token)

        self.bot: TelegramBot = TelegramBot(self.client, self.api_id, self.api_hash)

        self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        """Sets up command and callback event handlers for the bot."""
        self.client.add_event_handler(
            self.bot.start_handler, events.NewMessage(pattern=r"/start")
        )
        self.client.add_event_handler(
            self.bot.help_handler, events.NewMessage(pattern=r"/help")
        )
        self.client.add_event_handler(
            self.bot.subscribe_handler, events.NewMessage(pattern=r"/subscribe")
        )
        self.client.add_event_handler(
            self.bot.snos_handler, events.NewMessage(pattern=r"/ss")
        )
        self.client.add_event_handler(
            self.bot.status_handler, events.NewMessage(pattern=r"/status")
        )
        self.client.add_event_handler(
            self.bot.count_handler, events.NewMessage(pattern=r"/count")
        )
        self.client.add_event_handler(
            self.bot.add_admin_handler, events.NewMessage(pattern=r"/add_admin")
        )
        self.client.add_event_handler(
            self.bot.remove_admin_handler, events.NewMessage(pattern=r"/remove_admin")
        )

        self.client.add_event_handler(self.bot.callback_handler, events.CallbackQuery)

    def run(self) -> None:
        """Runs the bot until it is manually stopped or disconnected."""
        with self.client:
            try:
                print("Bot is running...")
                self.client.run_until_disconnected()
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    bot_instance = DrozloerBot()
    bot_instance.run()
