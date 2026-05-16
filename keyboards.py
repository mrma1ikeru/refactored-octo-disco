from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def categories_kb(categories, prefix):
    buttons = []

    for cat in categories:
        buttons.append([
            InlineKeyboardButton(
                text=cat,
                callback_data=f"{prefix}:{cat}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✏️ Своя категория",
            callback_data=f"{prefix}:custom"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)