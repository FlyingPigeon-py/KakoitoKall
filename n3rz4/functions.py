from telethon.tl.custom import Button
from n3rz4.base import User, session
from n3rz4.subscription import check_subscription
from n3rz4.reports import count_session, report_message
from datetime import datetime, timedelta


def millisecond_strip(time):
    return ":".join(str(time).split(".", 2)[:1])


class TelegramBot:
    def __init__(self, client, api_id, api_hash) -> None:
        self.client = client
        self.api_id = api_id
        self.api_hash = api_hash
        self.owners = [7497310837, 1781280002]
        self.admins = set(self.owners)
        self.users = {}
        self.subscription_text = (
            "💸 <b>Реквизиты для оплаты:</b>\n"
            "CryptoBot: <a href='http://t.me/send?start=IVffHIf23nSn'>ссылка на оплату</a>\n\n"
        )

    async def start_handler(self, msg) -> None:
        user_id = msg.sender_id
        if msg.chat_id != user_id:
            return

        user_entity = await self.client.get_entity(user_id)
        user = session.query(User).filter_by(id=user_id).first()

        if user is None:
            new_user = User(id=user_id, username=user_entity.username, status="")
            session.add(new_user)
            session.commit()
            user = new_user

        user = await check_subscription(user_id)
        subscription_status = (
            "⛔️ <b>Отсутствует</b>"
            if user.subscribe is None
            else f"✅ <b>Активна до</b> <code>{millisecond_strip(user.subscribe)}</code>."
        )

        text = (
            f"👋 Привет, @{user_entity.username}!\n\n"
            f"💼 <b>Ваш статус подписки:</b> {subscription_status}\n\n"
            f"💡 <i>Выберите нужную категорию ниже:</i>\n\n"
            f"📨 По всем вопросам: <b>@fenomenSS</b>"
        )
        image = "https://media1.tenor.com/m/e_MHf5Uye-oAAAAC/%D0%BA%D0%BE%D1%82-%D0%BC%D0%B5%D0%BC.gif"
        buttons = None
        if not user.subscribe:
            buttons = [[Button.inline("💳 Купить подписку", b"buy_subscription")]]
        await msg.reply(text, file=image, buttons=buttons, parse_mode="html")

    async def help_handler(self, msg) -> None:
        user_id = msg.sender_id
        user = await check_subscription(user_id)

        help_text = (
            "📄 <b>Список доступных команд:</b>\n\n"
            "<b>/start</b> — Перезапустить бота\n"
            "<b>/help</b> — Показать это сообщение\n"
            "<b>/status</b> — Показать информацию о подписке и запросах\n"
            "<b>/ss</b> <i>{ссылка на сообщение}</i> — Запустить снос аккаунта\n"
            "\n"
        )

        if user_id in self.admins or user.status == "admin":
            help_text += (
                "👑 <b>Административные команды:</b>\n\n"
                "<b>/count</b> — Посчитает и выведет количество активных сессий\n"
                "<b>/subscribe</b> <i>{id} {дней}</i> — Добавить подписку пользователю на определённое количество дней\n"
                "<b>/add_admin</b> <i>{id}</i> — Назначить пользователя администратором\n"
                "<b>/remove_admin</b> <i>{id}</i> — Удалить пользователя из администраторов\n"
                "\n"
            )

        help_text += "💬 Для дополнительных вопросов пишите <b>@fenomenSS</b>."
        await msg.reply(help_text, parse_mode="html")

    async def subscribe_handler(self, msg) -> None:
        user_id = msg.sender_id
        admin_user = session.query(User).filter_by(id=user_id).first()

        try:
            target_user_id, days = map(int, msg.message.message.split()[1:])
        except (ValueError, IndexError):
            await msg.reply(
                "⚠️ <b>Используйте формат:</b> /subscribe <i>{id} {дней}</i>",
                parse_mode="html",
            )
            return

        if user_id in self.admins or admin_user.status == "admin":
            await self._add_subscription(msg, target_user_id, days)
        else:
            await msg.reply(
                "❌ <b>У вас недостаточно прав для выполнения этой команды.</b>",
                parse_mode="html",
            )

    async def _add_subscription(self, msg, user_id, days) -> None:
        end_subscription = datetime.now() + timedelta(days=days)
        user = session.query(User).filter_by(id=user_id).first()

        if user:
            user.subscribe = end_subscription
            session.commit()
            user = await check_subscription(user_id)
            user_entity = await self.client.get_entity(user_id)

            await msg.reply(
                f"✅ <b>Пользователь <a href='tg://user?id={user_id}'>{user_entity.first_name}</a> "
                f"получил подписку до <code>{user.subscribe}</code>.</b>",
                parse_mode="html",
            )

            await self.client.send_message(
                user_id,
                f"✅ Ваша подписка активирована\nДействует до <code>{user.subscribe.strftime('%Y-%m-%d %H:%M:%S')}</code>.\n"
                "Теперь у вас есть доступ к 15 запросам в день.\n\nЕсли произошла какая-то ошибка то пишите <b>@fenomenSS</b>",
                parse_mode="html",
            )

        else:
            await msg.reply(
                "⚠️ <b>Этот пользователь не зарегистрирован. Попросите его написать /start в боте.</b>",
                parse_mode="html",
            )

    async def status_handler(self, msg) -> None:
        user_id = msg.sender_id
        user = await check_subscription(user_id)

        subscription_status = (
            "⛔️ <b>Подписка отсутствует</b>"
            if user.subscribe is None
            else f" ✅ Подписан\n\n⌛ <b>Подписка активна до:</b> <code>{millisecond_strip(user.subscribe)}</code>."
        )

        buttons = None
        if user.subscribe is None:
            buttons = [[Button.inline("💳 Купить подписку", b"buy_subscription")]]

        message = f"💼 <b>Ваш статус подписки:</b> {subscription_status}"
        if user.subscribe:
            message += f"\n\n📨 <b>Запросов доступно:</b> {user.get_requests()} (Обновиться через {millisecond_strip(user.get_time_until_reset())})"
        await msg.reply(
            message,
            buttons=buttons,
            parse_mode="html",
        )

    async def count_handler(self, msg) -> None:
        user_id = msg.sender_id
        if user_id in self.admins:
            bot_message = await msg.reply(
                "🔄<b>Подсчёт сессий запущен</b>",
                parse_mode="html",
            )
            try:
                count = await count_session(self.api_id, self.api_hash, bot_message)
                await bot_message.edit(
                    f"✅ <b>Общее кол-во сессий:</b> {count}",
                    parse_mode="html",
                )
            except Exception:
                await bot_message.edit(
                    "❌ Не удалось посчитать количество сессий", parse_mode="html"
                )
        else:
            await msg.reply(
                "❌ <b>Купите подписку для использования данной команды.</b>",
                parse_mode="html",
            )

    async def snos_handler(self, msg) -> None:
        try:
            link = msg.message.message.split(maxsplit=1)[1]
        except IndexError:
            await msg.reply(
                "⚠️ <b>Используйте формат:</b> /ss <i>{ссылка на сообщение}</i>",
                parse_mode="html",
            )
            return

        user_id = msg.sender_id
        user = await check_subscription(user_id)

        if user_id in self.admins or user.status == "admin" or user.subscribe:
            bot_message = await msg.reply(
                "🔄 <b>Процесс удаления аккаунта запущен. Пожалуйста, ожидайте завершения.</b>",
                parse_mode="html",
            )
            message = "✅ <b>Удаление завершено. Аккаунт будет заблокирован в ближайшее время.</b>"
            data = user.can_make_request()
            if not data["can_request"] and user_id not in self.admins:
                if user.get_requests() != 0:
                    message = f"⌛ <b>Подождите {':'.join(str(data['time_until_next_request']).split('.', 2)[:1])} перед следующим запросом</b>"
                else:
                    message = f"⌛ <b>Ваш запас в 15 запросов исчерпан, до восстановления {':'.join(str(data['time_until_reset']).split('.', 2)[:1])}</b>\n\nКупить больше запросы вы можете у @fenomenSS по 1.5$"
            else:
                try:
                    status = await report_message(link, self.api_id, self.api_hash)
                    if status == "ok":
                        user.spend_request()
                        message = f"✅ <b>Удаление завершено. Аккаунт будет заблокирован в ближайшее время.</b>\n\n📨 <b>Запросов доступно:</b> {user.get_requests()} (Обновиться через {millisecond_strip(user.get_time_until_reset())})"
                    elif status == "link_error":
                        message = "⚠️ <b>Указанна неправильная ссылка на сообщение</b>"
                    else:
                        message = "❌ <b>Во время удаления произошла непредвиденная ошибка</b>"
                except Exception:
                    message = "❌ <b>Во время удаления произошла непредвиденная ошибка</b>"

            await bot_message.edit(
                message,
                parse_mode="html",
            )
        else:
            await msg.reply(
                "❌ <b>Купите подписку для использования данной команды.</b>",
                parse_mode="html",
            )

    async def callback_handler(self, query) -> None:
        callbacks = {
            b"buy_subscription": self._show_subscription_options,
            b"week": self._show_subscription_confirmation,
            b"month": self._show_subscription_confirmation,
            b"year": self._show_subscription_confirmation,
            b"forever": self._show_subscription_confirmation,
            b"buy_admin": self._show_subscription_confirmation,
            b"back_to_buy_menu": self._show_subscription_options,
            b"back_to_menu": self._show_main_menu,
            b"confirm_the_purchase": self._confirm_purchase,
        }
        handler = callbacks.get(query.data)
        if handler:
            await handler(query)

    async def _show_subscription_options(self, query) -> None:
        buttons = [
            [Button.inline("🗓 Неделя", b"week"), Button.inline("📅 Месяц", b"month")],
            [
                Button.inline("📆 3 месяца", b"year"),
                Button.inline("📆 Пол года", b"buy_admin"),
            ],
            [
                Button.inline("📆 Год", b"forever"),
            ],
            [Button.inline("« Назад", b"back_to_menu")],
        ]
        await query.edit(
            "💳 <b>Выберите продолжительность подписки:</b>",
            buttons=buttons,
            parse_mode="html",
        )

    async def _show_subscription_confirmation(self, query) -> None:
        period = {
            b"week": ("Неделя", "500р / 5$"),
            b"month": ("Месяц", "800р / 8$"),
            b"year": ("3 месяца", "2000р / 20$"),
            b"forever": ("Пол года", "3500р / 35$"),
            b"buy_admin": ("Год", "5000р / 50$"),
        }

        period_name, price = period[query.data]
        user_id = query.sender_id
        self.users[user_id] = {query.data.decode(): period_name}

        buttons = [
            [Button.inline("☑️ Подтвердить покупку", b"confirm_the_purchase")],
            [Button.inline("« Назад", b"back_to_buy_menu")],
        ]
        await query.edit(
            self.subscription_text
            + f"<b>Вы выбрали:</b> {period_name}\n<b>Стоимость:</b> {price}",
            buttons=buttons,
            parse_mode="html",
        )

    async def _confirm_purchase(self, query) -> None:
        user_id = query.sender_id
        user_entity = await self.client.get_entity(user_id)
        username = user_entity.username or "NoUsername"

        package_info = self.users.get(user_id)

        if package_info:
            package_type = list(package_info.values())[0]
            confirmation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for owner_id in self.owners:
                await self.client.send_message(
                    owner_id,
                    (
                        f"📬 <b>Запрос на подтверждение оплаты</b>\n\n"
                        f"👤 <b>Пользователь:</b> <a href='tg://user?id={user_id}'>{username}</a>\n"
                        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
                        f"📅 <b>Время подтверждения:</b> <code>{confirmation_time}</code>\n"
                        f"💳 <b>Тариф:</b> {package_type}\n\n"
                        "🚨 Пожалуйста, проверьте и подтвердите оплату."
                    ),
                    parse_mode="html",
                )

        await query.edit(
            "✅ <b>Запрос на подтверждение оплаты отправлен!</b>\n💬 <i>Администрация скоро обработает ваш запрос.</i>",
            parse_mode="html",
        )

    async def _show_main_menu(self, query) -> None:
        user_id = query.sender_id
        user = await check_subscription(user_id)
        subscription_status = (
            "⛔️ <b>Подписка отсутствует</b>"
            if user.subscribe is None
            else f"✅ <b>Подписка активна до:</b> <code>{user.subscribe}</code>."
        )

        buttons = [[Button.inline("💳 Купить подписку", b"buy_subscription")]]
        await query.edit(
            f"💼 <b>Ваш статус подписки:</b> {subscription_status}\n\n"
            f"📝 Выберите категорию из предложенных ниже.",
            buttons=buttons,
            parse_mode="html",
        )

    async def add_admin_handler(self, msg) -> None:
        user_id = msg.sender_id
        admin_user = session.query(User).filter_by(id=user_id).first()

        try:
            new_admin_id = int(msg.message.message.split()[1])
        except (ValueError, IndexError):
            await msg.reply(
                "⚠️ <b>Используйте формат:</b> /add_admin {id}", parse_mode="html"
            )
            return

        if user_id in self.admins or admin_user.status == "admin":
            if new_admin_id not in self.admins:
                self.admins.add(new_admin_id)
                await msg.reply(
                    f"✅ <b>Пользователь <a href='tg://user?id={new_admin_id}'>{new_admin_id}</a> добавлен как администратор.</b>",
                    parse_mode="html",
                )
            else:
                await msg.reply(
                    "⚠️ <b>Этот пользователь уже является администратором.</b>",
                    parse_mode="html",
                )
        else:
            await msg.reply(
                "❌ <b>У вас недостаточно прав для выполнения этой команды.</b>",
                parse_mode="html",
            )

    async def remove_admin_handler(self, msg) -> None:
        user_id = msg.sender_id
        admin_user = session.query(User).filter_by(id=user_id).first()

        try:
            admin_id = int(msg.message.message.split()[1])
        except (ValueError, IndexError):
            await msg.reply(
                "⚠️ <b>Используйте формат:</b> /remove_admin {id}", parse_mode="html"
            )
            return

        if user_id in self.admins or admin_user.status == "admin":
            if admin_id in self.admins:
                self.admins.remove(admin_id)
                await msg.reply(
                    f"✅ <b>Пользователь <a href='tg://user?id={admin_id}'>{admin_id}</a> удалён из администраторов.</b>",
                    parse_mode="html",
                )
            else:
                await msg.reply(
                    "⚠️ <b>Этот пользователь не является администратором.</b>",
                    parse_mode="html",
                )
        else:
            await msg.reply(
                "❌ <b>У вас недостаточно прав для выполнения этой команды.</b>",
                parse_mode="html",
            )
