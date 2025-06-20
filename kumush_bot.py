from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# 🔒 Sizning admin Telegram ID (bot sizga buyurtma yuboradi)
ADMIN_ID = 8033544252

# 🛍️ Mahsulotlar qo'lda kiritiladi
products = {
    "ring": {"name": "💍 Ayollar uzugi", "price": 120000, "desc": "925 kumush, toshli"},
    "bracelet": {"name": "🪙 Erkaklar bilakuzugi", "price": 150000, "desc": "Og'irligi: 22g"},
    "earring": {"name": "✨ Sirg‘a", "price": 100000, "desc": "Oddiy model, 5g"}
}

# 👤 Har bir user uchun savatcha
user_carts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for key, product in products.items():
        button = InlineKeyboardButton(f"{product['name']} - {product['price']} so'm", callback_data=f"buy_{key}")
        keyboard.append([button])
    keyboard.append([InlineKeyboardButton("🛒 Savatni ko‘rish", callback_data="cart")])
    await update.message.reply_text("Quyidagi mahsulotlardan birini tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data.startswith("buy_"):
        item_key = query.data.split("_")[1]
        if user_id not in user_carts:
            user_carts[user_id] = []
        user_carts[user_id].append(item_key)
        await query.edit_message_text(f"{products[item_key]['name']} savatchaga qo‘shildi!")

    elif query.data == "cart":
        cart = user_carts.get(user_id, [])
        if not cart:
            await query.edit_message_text("🛒 Savat bo‘sh.")
        else:
            text = "🛒 Savat:\n"
            total = 0
            for key in cart:
                p = products[key]
                text += f"• {p['name']} - {p['price']} so'm\n"
                total += p['price']
            text += f"\n💰 Jami: {total} so'm\n\n📲 Telefon raqamingizni yuboring:"
            await query.edit_message_text(text)
            context.user_data["awaiting_phone"] = True

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_phone"):
        phone = update.message.text
        user_id = update.message.from_user.id
        cart = user_carts.get(user_id, [])

        if not cart:
            await update.message.reply_text("Savat bo‘sh.")
            return

        # 📦 Buyurtma tafsilotlari
        text = "📥 Yangi buyurtma:\n"
        for key in cart:
            p = products[key]
            text += f"• {p['name']} - {p['price']} so'm\n"
        total = sum(products[k]['price'] for k in cart)
        text += f"\n💰 Jami: {total} so'm\n📞 Telefon: {phone}\n👤 @{update.message.from_user.username or 'Ismi yo‘q'}"

        # 🔔 Admin (sizga) yuboriladi
        await context.bot.send_message(chat_id=ADMIN_ID, text=text)

        # ✅ Foydalanuvchiga tasdiq
        await update.message.reply_text("✅ Buyurtmangiz qabul qilindi. Tez orada siz bilan bog‘lanamiz.")
        user_carts[user_id] = []
        context.user_data["awaiting_phone"] = False

def main():
    app = Application.builder().token("8033544252:AAGECAosAOlVDaYXyF4R2s7HBBIrUQwOQX4").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler))

    print("💎 Kumush bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
