from telethon import events

def register(client, owner_id=None):
    """
    Команды:
    .люблю               — отправит blockquote с "Я люблю тебя"
    .люблю <эмодзи/текст> — добавит после цитаты указанный текст или эмодзи
    Пример: .люблю 🫶
    """
    @client.on(events.NewMessage(pattern=r"^\.люблю(?: |$)(.*)"))
    async def iloveyou(event):
        arg = (event.pattern_match.group(1) or "").strip()
        # Форматируем как Markdown blockquote (строка, начинающаяся с ">")
        text = "> Я люблю тебя"
        if arg:
            text = f"{text}\n{arg}"
        await event.reply(text, parse_mode='md')