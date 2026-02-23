import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Bot sozlamalari
BOT_TOKEN = "8348120302:AAFBDaQVqYZeTWIvKXAQXg7ko09GxrAcWTk"
ADMIN_ID = 5204435903

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Holatlar (States)
class Registration(StatesGroup):
    waiting_fio_latin = State()
    waiting_fio_cyrillic = State()
    waiting_region = State()
    waiting_district = State()
    waiting_position = State()
    waiting_phone = State()
    waiting_passport = State()
    waiting_password = State()
    confirm_data = State()

class AdminApproval(StatesGroup):
    waiting_admin_login = State()
    waiting_admin_password = State()

# Klaviaturalar
def get_yes_no_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Ha")
    builder.button(text="Yo'q")
    return builder.as_markup(resize_keyboard=True)

# /start komandasi
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Assalomu alaykum! Xodimlarni ro'yxatdan o'tkazish botiga xush kelibsiz.\n\nRo'yxatdan o'tishni boshlash uchun F.I.Sh (Familiya, Ism, Sharif)ingizni lotin harflarida kiriting:")
    await state.set_state(Registration.waiting_fio_latin)

# FIO Latin
@dp.message(Registration.waiting_fio_latin)
async def process_fio_latin(message: types.Message, state: FSMContext):
    await state.update_data(fio_latin=message.text)
    await message.answer("F.I.Sh (Familiya, Ism, Sharif)ingizni kiril harflarida kiriting:")
    await state.set_state(Registration.waiting_fio_cyrillic)

# FIO Cyrillic
@dp.message(Registration.waiting_fio_cyrillic)
async def process_fio_cyrillic(message: types.Message, state: FSMContext):
    await state.update_data(fio_cyrillic=message.text)
    await message.answer("Viloyatingizni kiriting:")
    await state.set_state(Registration.waiting_region)

# Region
@dp.message(Registration.waiting_region)
async def process_region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)
    await message.answer("Tumaningizni kiriting:")
    await state.set_state(Registration.waiting_district)

# District
@dp.message(Registration.waiting_district)
async def process_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await message.answer("Lavozimingizni kiriting:")
    await state.set_state(Registration.waiting_position)

# Position
@dp.message(Registration.waiting_position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(Registration.waiting_phone)

# Phone
@dp.message(Registration.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Pasport seriyasi va raqamingizni kiriting:")
    await state.set_state(Registration.waiting_passport)

# Passport
@dp.message(Registration.waiting_passport)
async def process_passport(message: types.Message, state: FSMContext):
    await state.update_data(passport=message.text)
    await message.answer("O'zingiz uchun parol yarating:")
    await state.set_state(Registration.waiting_password)

# Password
@dp.message(Registration.waiting_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    
    summary = (
        f"Kiritilgan ma'lumotlarni tekshiring:\n\n"
        f"F.I.Sh (Lotin): {data['fio_latin']}\n"
        f"F.I.Sh (Kiril): {data['fio_cyrillic']}\n"
        f"Viloyat: {data['region']}\n"
        f"Tuman: {data['district']}\n"
        f"Lavozim: {data['position']}\n"
        f"Telefon: {data['phone']}\n"
        f"Pasport: {data['passport']}\n"
        f"Parol: {data['password']}\n\n"
        f"Ma'lumotlar to'g'rimi?"
    )
    
    await message.answer(summary, reply_markup=get_yes_no_kb())
    await state.set_state(Registration.confirm_data)

# Tasdiqlash
@dp.message(Registration.confirm_data, F.text == "Ha")
async def process_confirm_yes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    # Administratorga yuborish
    admin_msg = (
        f"Yangi ariza keldi!\n\n"
        f"F.I.Sh (Lotin): {data['fio_latin']}\n"
        f"F.I.Sh (Kiril): {data['fio_cyrillic']}\n"
        f"Viloyat: {data['region']}\n"
        f"Tuman: {data['district']}\n"
        f"Lavozim: {data['position']}\n"
        f"Telefon: {data['phone']}\n"
        f"Pasport: {data['passport']}\n"
        f"Xodim paroli: {data['password']}\n"
        f"User ID: {message.from_user.id}"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Tasdiqlash", callback_data=f"approve_{message.from_user.id}")
    builder.button(text="Rad etish", callback_data=f"reject_{message.from_user.id}")
    
    await bot.send_message(ADMIN_ID, admin_msg, reply_markup=builder.as_markup())
    
    await message.answer("Arizangiz administratorga yuborildi. Iltimos, tasdiqlashni kuting.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@dp.message(Registration.confirm_data, F.text == "Yo'q")
async def process_confirm_no(message: types.Message, state: FSMContext):
    await message.answer("Ro'yxatdan o'tish bekor qilindi. Qaytadan boshlash uchun /start bosing.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

# Administrator uchun callbacklar
@dp.callback_query(F.data.startswith("approve_"))
async def admin_approve(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split("_")[1]
    await state.update_data(target_user_id=user_id)
    await callback.message.answer(f"Xodim (ID: {user_id}) uchun yangi LOGIN kiriting:")
    await state.set_state(AdminApproval.waiting_admin_login)
    await callback.answer()

@dp.message(AdminApproval.waiting_admin_login)
async def process_admin_login(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(new_login=message.text)
    await message.answer("Endi yangi PAROL kiriting:")
    await state.set_state(AdminApproval.waiting_admin_password)

@dp.message(AdminApproval.waiting_admin_password)
async def process_admin_password(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    new_login = data['new_login']
    new_password = message.text
    target_user_id = data['target_user_id']
    
    # Xodimga yuborish
    await bot.send_message(
        target_user_id,
        f"Tabriklaymiz! Arizangiz tasdiqlandi.\n\nSizning login va parolingiz:\nLogin: {new_login}\nParol: {new_password}"
    )
    
    await message.answer(f"Xodimga (ID: {target_user_id}) login va parol yuborildi.")
    await state.clear()

@dp.callback_query(F.data.startswith("reject_"))
async def admin_reject(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await bot.send_message(user_id, "Afsuski, sizning arizangiz administrator tomonidan rad etildi.")
    await callback.message.answer(f"Xodim (ID: {user_id}) arizasi rad etildi.")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
