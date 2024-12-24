import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن الخاص بك
TOKEN = "7732932703:AAEzzIKl1d1Wf38CWohZgc8-_7jKto54APA"

# اسم القناة للاشتراك الإجباري
CHANNEL_USERNAME = "@animeurea"

# دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك! فقط أرسل صورة من الأنمي وسأساعدك في البحث عن تفاصيله. ✅"
    )

# تحقق من الاشتراك
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        print(f"Error checking subscription: {e}")
    await update.message.reply_text(
        "يرجى الاشتراك في القناة @animeurea لاستخدام البوت. ✅"
    )
    return False

# البحث عن صورة باستخدام Google Images
async def search_google_images(image_url):
    search_url = "https://www.google.com/searchbyimage"
    params = {
        "image_url": image_url,
        "encoded_image": "",
        "image_content": "",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # إرسال الطلب إلى Google
    response = requests.get(search_url, params=params, headers=headers)
    if response.status_code != 200:
        return None

    # تحليل الصفحة باستخدام BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("a", class_="BVG0Nb")
    links = [{"title": res.get_text(), "link": res["href"]} for res in results]

    return links

# دالة لمعالجة الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_url = file.file_path

    # البحث باستخدام Google Images
    results = await search_google_images(image_url)
    if not results:
        await update.message.reply_text("عذرًا، لم أتمكن من العثور على أي نتائج للصورة. 😔")
        return

    # إرسال النتائج إلى المستخدم
    reply_text = "تم العثور على النتائج التالية:\n\n"
    for result in results[:5]:  # عرض أول 5 نتائج
        reply_text += f"- [{result['title']}]({result['link']})\n"
    await update.message.reply_text(reply_text, parse_mode="Markdown")

# الإعدادات الرئيسية
def main():
    application = Application.builder().token(TOKEN).build()

    # ربط الأوامر والمستقبلات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # تشغيل البوت
    application.run_polling()

if __name__ == "__main__":
    main()
