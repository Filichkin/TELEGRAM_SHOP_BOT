from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import UserDAO
from bot.user.kbs import main_user_kb, user_services_kb
from bot.user.schemas import TelegramIDModel, UserModel


user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=user_id)
    )

    if user_info:
        return await message.answer(
            'Выберите необходимое действие:',
            reply_markup=main_user_kb(user_id)
        )

    values = UserModel(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await UserDAO.add(session=session_with_commit, values=values)
    await message.answer(
        '🎉 <b>Благодарим за регистрацию!</b>. '
        'Теперь выберите необходимое действие.',
        reply_markup=main_user_kb(user_id)
    )


@user_router.callback_query(F.data == 'home')
async def page_home(call: CallbackQuery):
    await call.answer('Главная страница')
    return await call.message.answer(
        'Выберите необходимое действие:',
        reply_markup=main_user_kb(call.from_user.id)
    )


@user_router.callback_query(F.data == 'about')
async def page_about(call: CallbackQuery):
    await call.answer('О сервисах')
    await call.message.answer(
        text=(
            '🚗 Перевернуть локальный VIN\n\n'
            '🛞 Узнать наличие запчасти по артикулу.\n\n'
            '⚙️ Проверить историю ТО.\n\n'
            '👨‍🔧 Поговорить с  консультантом\n'
        ),
        reply_markup=call.message.reply_markup
    )


@user_router.callback_query(F.data == 'my_profile')
async def page_user_profile(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Профиль')

    # Получаем покупки пользователя
    payments = await UserDAO.get_purchased_services(
            session=session_without_commit,
            telegram_id=call.from_user.id
            )

    # Формируем сообщение в зависимости от наличия покупок
    if payments == 0:
        await call.message.answer(
            text='🔍 <b>У вас пока нет оплаченных сервисов.</b>\n\n'
                 'Откройте каталог и выберите нужный сервис!',
            reply_markup=main_user_kb(call.from_user.id)
        )
    else:
        # Формируем список оплаченных сервисов.
        services = [payment.service for payment in payments]
        await call.message.edit_text(
            text='Выберите сервис:',
            reply_markup=user_services_kb(services)
        )


@user_router.callback_query(F.data == 'payments')
async def page_user_payments(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Мои оплаты')

    # Получаем список покупок пользователя.
    payments = await UserDAO.get_purchased_services(
        session=session_without_commit,
        telegram_id=call.from_user.id
        )
    payments_statistic = await UserDAO.get_purchase_statistics(
        session=session_without_commit,
        telegram_id=call.from_user.id
        )
    total_amount = payments_statistic.get('total_amount', 0)
    total_payments = payments_statistic.get('count_payments', 0)

    if not payments:
        await call.message.edit_text(
            text='🔍 <b>У вас пока нет оплат.</b>\n\n'
                 'Откройте каталог и выберите нужный сервис!',
            reply_markup=main_user_kb(call.from_user.id)
        )
        return
    statistic_text = (
            f'🚗  <b>Ваш профиль:</b>\n\n'
            f'Количество покупок: <b>{total_payments}</b>\n'
            f'Общая сумма: <b>{total_amount}₽</b>\n\n'
            'Хотите просмотреть детали ваших оплат?'
        )
    await call.message.answer(text=statistic_text)

    # Для каждой оплаты отправляем информацию.
    for payment in payments:
        service = payment.service

        service_text = (
            f'🛒 <b>Информация о вашем сервисе:</b>\n'
            f'━━━━━━━━━━━━━━━━━━\n'
            f'🔹 <b>Название:</b> <i>{service.name}</i>\n'
            f'🔹 <b>Описание:</b>\n<i>{service.description}</i>\n'
            f'🔹 <b>Цена:</b> <b>{service.price} ₽</b>\n'
            f'🔹 <b>Закрытое описание:</b>\n<i>{service.hidden_content}</i>\n'
            f"━━━━━━━━━━━━━━━━━━\n"
        )
        await call.message.answer(text=service_text)

    await call.message.answer(
        text='Для продолжения работы, выберите необходимое действие:',
        reply_markup=main_user_kb(call.from_user.id)
    )
