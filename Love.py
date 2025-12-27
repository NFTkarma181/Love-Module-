"""
telethon_love_register_module.py
Простой модуль для Telethon userbot.
Экспортирует функцию register(client) — требование некоторых Heroku loader'ов.
Команда: .люблю [эмодзи]
Отправляет как blockquote: "> Я люблю тебя" + опциональный эмодзи
"""
import sys

try:
    from telethon import events
except Exception as e:
    # Telethon недоступен в момент импорта — регистрироваться будем терпимо
    events = None
    print(f"[love_module] Telethon import failed: {e}")

_PATTERN = r'^\.люблю(?:\s+(.*))?$'


async def _love_handler(event):
    """Корутина-обработчик Telethon"""
    emoji = ''
    try:
        if hasattr(event, 'pattern_match') and event.pattern_match:
            emoji = (event.pattern_match.group(1) or '').strip()
    except Exception:
        emoji = ''
    if not emoji:
        try:
            txt = (getattr(event.message, 'message', '') or '')
            parts = txt.split(maxsplit=1)
            emoji = parts[1].strip() if len(parts) > 1 else ''
        except Exception:
            emoji = ''

    text = '> Я люблю тебя'
    if emoji:
        text += ' ' + emoji

    try:
        await event.respond(text)
    except Exception:
        try:
            await event.reply(text)
        except Exception:
            print("[love_module] Failed to send message (respond/reply both failed).")

    try:
        await event.delete()
    except Exception:
        # игнорируем, если нельзя удалить
        pass


def register(client):
    """
    Обязательная функция для loader'а.
    client — экземпляр Telethon TelegramClient или объект с add_event_handler.
    Возвращает True при успешной регистрации, False иначе.
    """
    if events is None:
        print("[love_module] Telethon недоступен — регистрация невозможна.")
        return False

    if client is None:
        print("[love_module] register: client is None.")
        return False

    try:
        add = getattr(client, 'add_event_handler', None)
        if callable(add):
            add(_love_handler, events.NewMessage(outgoing=True, pattern=_PATTERN))
            print("[love_module] Обработчик зарегистрирован через add_event_handler().")
            return True

        # Иногда используются другие интерфейсы (на всякий случай)
        on = getattr(client, 'on', None)
        if callable(on):
            on(events.NewMessage(outgoing=True, pattern=_PATTERN))(_love_handler)
            print("[love_module] Обработчик зарегистрирован через on().")
            return True

    except Exception as e:
        print(f"[love_module] Ошибка при регистрации обработчика: {e}")
        return False

    print("[love_module] Клиент не предоставляет add_event_handler или on — регистрация невозможна.")
    return False


# Мягкая автоматическая попытка регистрации при импорте (если loader НЕ вызывает register)
def _is_probable_client(obj):
    if obj is None:
        return False
    if hasattr(obj, 'add_event_handler') and callable(getattr(obj, 'add_event_handler')):
        return True
    if hasattr(obj, 'send_message') and callable(getattr(obj, 'send_message')):
        return True
    return False


def _find_client_once():
    # 1) Проверить globals текущего окружения
    for name in ('bot', 'client', 'app', 'tbot', 'userbot', 'ubot'):
        val = globals().get(name)
        if _is_probable_client(val):
            print(f"[love_module] Найден клиент в globals() как '{name}'")
            return val
    # 2) Проверить __main__
    main = sys.modules.get('__main__')
    if main:
        for name in ('bot', 'client', 'app', 'tbot', 'userbot', 'ubot'):
            val = getattr(main, name, None)
            if _is_probable_client(val):
                print(f"[love_module] Найден клиент в __main__ как '{name}'")
                return val
    # 3) Сканировать загруженные модули
    for module in list(sys.modules.values()):
        if not module:
            continue
        try:
            for attr_name, attr_val in vars(module).items():
                if _is_probable_client(attr_val):
                    print(f"[love_module] Найден клиент в модуле '{getattr(module, '__name__', 'unknown')}' атрибут '{attr_name}'")
                    return attr_val
        except Exception:
            continue
    return None


try:
    _auto_client = _find_client_once()
    if _auto_client:
        try:
            ok = register(_auto_client)
            if not ok:
                print("[love_module] Автоматическая регистрация нашла клиент, но регистрация не удалась.")
        except Exception as e:
            print(f"[love_module] Ошибка при автоматической регистрации: {e}")
except Exception as e:
    print(f"[love_module] Ошибка поиска клиента при импорте: {e}")
