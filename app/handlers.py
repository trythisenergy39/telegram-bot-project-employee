import app.keybords as kb
from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from app.db import get_session
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy import update
from app.models import Employer, Support, Postings
from app.db import async_session
from config import config
from urllib.parse import quote
from app.filters import Admin, AdminC
from aiogram.fsm.context import FSMContext
from app.States import pbr_cl
from app.States import ibr_cl
from app.States import posting_id_accept, posting_accept_cost, sca, posting_accept_text, date_accept_cost, posting_id_date, posting_date_text, prodlite, prodlit1
from decimal import Decimal
from app.db import delete_post
from dateutil.relativedelta import relativedelta
from datetime import date

router = Router()



#Начало обработки команды старт/выбор статуса (п.1,2,3)
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(F"Приветственное сообщение")
    await message.answer('Перейти к выбору статуса?', reply_markup=kb.choose_status)
#Конец обработки команды старт

@router.callback_query(F.data == 'status')
async def status(callback: CallbackQuery):
    await callback.message.answer('Информация о возможных статусах пользователя', reply_markup=kb.choose_role)

#Начало обработки команды выбора статуса пользователя: работодатель/Инструкция/предложение выбрать продукт (п.4,5)/добавление пользователя в базу данных работодателей
@router.callback_query(F.data == 'employer')
async def employer_status(callback: CallbackQuery):
    userid = callback.from_user.id
    userid = int(userid)
    u_name = callback.from_user.first_name
    cash = 0
    posting_counter = 0
    help_message_counter = 0
    reting_employer = 0
    returns_counter = 0

    await callback.message.answer('Ссылка на инструкцию и предложение приступить к выбору продукта',
                     reply_markup=kb.goto_choose_product)
    # Проверка есть ли пользователь в базе данных
    try:
        async with async_session() as session:
            existing_user = await session.get(Employer, userid)


# Условие (если да ничего не делать, если нет добавить его данные)
            if existing_user:
                stmt = update(Employer).where(Employer.user_id == userid).values(user_name=u_name)
                await session.execute(stmt)
                await session.commit()

            else:
                new_employer = Employer(
                    user_id=userid,
                    cash=cash,
                    posting_counter=posting_counter,
                    help_message_counter=help_message_counter,
                    user_name=u_name,
                    reting_employer=reting_employer,
                    returns_counter=returns_counter
                )
                session.add(new_employer)
                await session.commit()

    except Exception as e:
        await callback.message.answer( f"Ошибка запроса, попробуйте еще раз. Код ошибки: {e}")
        return

#Обработка команды выбора статуса пользователя: Работодатель/Выбор продукта (п.6,7)
@router.callback_query(F.data == 'employer_choose_product')
async def employer_choose_product(callback: CallbackQuery):
    await callback.message.answer('Информация об услугах для работодателя', reply_markup=kb.employer_product)

#Обработка команды выбора статуса пользователя: Работодатель/Продукт
@router.callback_query(F.data == 'empl_Product_1')
async def empl_Product_1(callback: CallbackQuery, bot: Bot):
        user_id = callback.from_user.id
        clbk = 1
        user_link = f"tg://user?id={user_id}"
        admin_message = (f"Пользователь {user_link} выбрал Продукт №{clbk}, номер счёта для пополнения: {user_id}")
        keyboard = kb.empl_get_product_keyboard(clbk, user_id)
        await callback.message.answer('Одобрительное сообщение для пользователя с предложением связаться с нами', reply_markup=keyboard)
        await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=admin_message)

#Обработка команды выбора статуса пользователя: Работодатель/Продукт 2
@router.callback_query(F.data == 'empl_Product_2')
async def empl_Product_2(callback: CallbackQuery, bot: Bot):
        user_id = callback.from_user.id
        clbk = 2
        user_link = f"tg://user?id={user_id}"
        admin_message = (f"Пользователь {user_link} выбрал Продукт №{clbk}, номер счёта для пополнения: {user_id}")
        keyboard = kb.empl_get_product_keyboard(clbk, user_id)
        await callback.message.answer('Одобрительное сообщение для пользователя с предложением связаться с нами', reply_markup=keyboard)
        await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=admin_message)

#Пополнение баланса
@router.message(Command("pbr"), Admin())
async def pbr_command(message: Message, state: FSMContext):
    await state.set_state(pbr_cl.user_id)
    await message.answer('Введите ID Пользователя которому хотите пополнить баланс')

@router.message(pbr_cl.user_id, Admin())
async def pbr_step2(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await state.set_state(pbr_cl.summ)
        data = await state.get_data()
        await message.answer(f'Введите сумму на которую необходимо пополнить баланс пользователю: tg://user?id={data["user_id"]}')
    except ValueError:
        await state.update_data(user_id=None)
        await message.answer('ID должен быть числом, введите заново')


@router.message(pbr_cl.summ, Admin())
async def pbr_step3(message: Message, state: FSMContext, bot: Bot):
    summm = int(message.text)
    await state.update_data(summ=summm)
    data = await state.get_data()
    user_id = int(data["user_id"])
    summ = int(data["summ"])
    try:
        summ = int(message.text)
        await state.update_data(summ=summ)

    except ValueError:
        await state.update_data(summ=None)
        await message.answer('Сумма должен быть числом')

    try:

        async with async_session() as session:
            existing_user = await session.get(Employer, data["user_id"])

            if existing_user:
                stmt = update(Employer).where(Employer.user_id == user_id).values(cash=Employer.cash+summ)
                await session.execute(stmt)
                await session.commit()
                await message.answer(f'Баланс пользователя ({user_id}) успешно изменён на {summ}')
                async with async_session() as session:
                    uc = await session.get(Employer, user_id)
                await bot.send_message(chat_id=user_id, text=f'Ваш счёт был пополнен на: {summ}. Текущий баланс: {uc.cash}', reply_markup=kb.employer_choose_posting_cost)
                await state.clear()

            else:
                await message.answer('Такого пользователя не существует, воспользуйтесь командой заново')
                await state.clear()

    except Exception as e:
        await message.answer(f'❌ Произошла ошибка: {e}, повторно вызовите команду')
        await state.clear()

@router.message(Command("set_cost_accept"), Admin())
async def set_cost_accept(message: Message, state: FSMContext):
    await state.set_state(sca.set_cost)
    await message.answer('Введите цену на один отклик')

@router.message(sca.set_cost, Admin())
async def set_cost_accept2(message: Message, state: FSMContext):
    try:
        set_cost = int(message.text)
        await state.update_data(set_cost=set_cost)
        await state.set_state(sca.k_dscnt)
        await message.answer('Введите коэффциент скидки от 0 до 1 с точностью до 2 знаков после запятой, не более')
    except ValueError:
        await state.update_data(set_cost=None)
        await message.answer('Цена должна быть числом')
        return

@router.message(sca.k_dscnt, Admin())
async def set_cost_accept3(message: Message, state: FSMContext):
    try:
        k_dscnt = Decimal(message.text).quantize(Decimal("0.01"))
        await state.update_data(k_dscnt=k_dscnt)
        await state.set_state(sca.week)
        await message.answer('Введите цену за одну неделю публикации')

    except ValueError:
        await state.update_data(k_dscnt=None)
        await message.answer('Введите коэффциент скидки от 0 до 1 с точностью до 2 знаков после запятой, не более')
        return

@router.message(sca.week, Admin())
async def set_cost_accept4(message: Message, state: FSMContext):
    cw = int(message.text)
    await state.update_data(week=cw)
    try:
        data = await state.get_data()
        k_dsc = Decimal(data['k_dscnt']).quantize(Decimal("0.01"))
        set_cst = int(data["set_cost"])
        sup_id = 1
        cw = int(data['week'])
        async with async_session() as session:
            existing_user = await session.get(Support, sup_id)

            if existing_user:
                stmt = update(Support).where(Support.sup_id == sup_id).values(cost_view=set_cst, k_dscnt=k_dsc, cost_week=cw)
                await session.execute(stmt)
                await session.commit()

            else:
                new_cost = Support(
                    cost_view=set_cst,
                    k_dscnt=k_dsc,
                )
                session.add(new_cost)
                await session.commit()
        await state.clear()
        await message.answer(f'Цена на один отклик установлена ({set_cst}) Скидка:  {(1-k_dsc) * 100}%, Цена за неделю: {cw}')

    except Exception as e:
        await message.answer(f'❌ Произошла ошибка: {e}, повторно вызовите команду')
        await state.clear()

#Изменение баланса
@router.message(Command("ibr"), Admin())
async def ibr_command(message: Message, state: FSMContext):
    await state.set_state(ibr_cl.user_id)
    await message.answer('Введите ID Пользователя которому хотите пополнить баланс')

@router.message(ibr_cl.user_id, Admin())
async def ibr_step2(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await state.set_state(ibr_cl.summ)
        data = await state.get_data()
        await message.answer(f'Введите сумму на которую необходимо изменить баланс пользователю: tg://user?id={data["user_id"]}')
    except ValueError:
        await state.update_data(user_id=None)
        await message.answer('ID должен быть числом, введите заново')


@router.message(ibr_cl.summ, Admin())
async def ibr_step3(message: Message, state: FSMContext, bot: Bot):
    try:
        summ = int(message.text)
        await state.update_data(summ=summ)

    except ValueError:
        await state.update_data(summ=None)
        await message.answer('Сумма должен быть числом')

    try:
        data = await state.get_data()
        user_id = int(data["user_id"])
        summ = int(data["summ"])
        async with async_session() as session:
            existing_user = await session.get(Employer, data["user_id"])

            if existing_user:
                stmt = update(Employer).where(Employer.user_id == user_id).values(cash=summ)
                await session.execute(stmt)
                await session.commit()
                await message.answer(f'Баланс пользователя ({user_id}) успешно изменён на {summ}')
                async with async_session() as session:
                    uc = await session.get(Employer, user_id)
                    await session.commit()
                await bot.send_message(chat_id=user_id, text=f'Ваш счёт был изменён на: {summ}. Текущий баланс: {uc.cash}', reply_markup=kb.employer_choose_posting_cost)
                await state.clear()

            else:
                await message.answer('Такого пользователя не существует, воспользуйтесь командой заново')
                await state.clear()

    except Exception as e:
        await message.answer(f'❌ Произошла ошибка: {e}, повторно вызовите команду')
        await state.clear()

#Команда для проверки баланса пользователя(работодатель)
@router.message(Command("balance"))
async def balance(message: Message):
    user_id = message.from_user.id
    try:
        async with async_session() as session:
            uc = await session.get(Employer, user_id)
            await session.commit()
        await message.answer(f'Ваш баланс: {uc.cash} откликов')
    except Exception as e:
        await message.answer(f'❌ Произошла ошибка: {e}. Возможно вы еще не пополняли счёт')

@router.message(Command("create"))
async def create(message: Message):
    user_id = message.from_user.id
    accept = False
    date_accept = False
    async with async_session() as session:
        try:
                stmt = select(Postings).where(Postings.user_id == user_id)
                result = await session.execute(stmt)
                rows = result.scalars().all()
                if not rows:
                    user = await session.get(Employer, user_id)
                    cash = int(user.cash)
                    if cash > 0:
                        keyboard = kb.employer_choose_posting_cost
                        await message.answer('Нет активных объявлений. Перейти к покупкам?', reply_markup=keyboard)
                    else:
                        keyboards = kb.goto_choose_product
                        await message.answer('Нет активных объявлений. Перейти к покупкам?', reply_markup=keyboards)
                    return
        except Exception as e:
            await message.answer(f"Ошибка при получении данных: {e}.")
            return

        try:
                stmt_accept = select(Postings).where(and_(Postings.user_id == user_id, Postings.life_time_accept > 0, Postings.active == 0))
                result = await session.execute(stmt_accept)
                rows = result.scalars().all()
                if rows:
                    posting_ids = [row.posting_id for row in rows]
                    await message.answer('Выберите объявление которое хотите редактировать по количеству принятых', reply_markup=await kb.postings_id_a(posting_ids))
                    accept = True
                stmt_date = select(Postings).where(and_(Postings.user_id == user_id, Postings.life_time_date.is_not(None), Postings.active == 0))
                result1 = await session.execute(stmt_date)
                rows1 = result1.scalars().all()
                if rows1:
                    posting_idss = [row.posting_id for row in rows1]
                    await message.answer('Выберите объявление которое хотите редактировать по дате',
                                         reply_markup=await kb.postings_id_d(posting_idss))
                    date_accept = True
                if not date_accept and not accept:
                    await message.answer('У вас нет активных объявлений которые можно отредактировать')
        except Exception as e:
            await message.answer(f'Ошибка. Код ошибки: {e}')
            return

#Обработка команды покупки работодателем объявления/выбор продукта
@router.callback_query(F.data == 'employer_choose_posting_cost')
async def employer_choose_posting_cost(callback: CallbackQuery):
    await callback.message.answer("Каталог предложений со списком жизни объявлений и кнопками купить", reply_markup=kb.emp_by_prod)

#Обработка команды подтверждения выбора/по количеству принятых
@router.callback_query(F.data == 'empl_view_value')
async def empl_view_value(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Вы выбрали продукт ограниченный по количеству принятых?,Введите количество откликов, которые хотите приобрести")

    await state.set_state(posting_accept_cost.life_time_accept)
#Обработка покупки и создания объявления по количеству принятых
@router.message(posting_accept_cost.life_time_accept)
async def pac(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректное число. Например: 3 или 777")
        return
    life_time_accept = message.text
    await state.update_data(life_time_accept=life_time_accept)
    data = await state.get_data()
    life_time_accepts = int(data["life_time_accept"])
    await state.clear()
    try:
        async with async_session() as session:
            cst = await session.execute(select(Support))
            ccst = cst.scalars().first()
            if ccst:
                cost = ccst.cost_view
                discount = ccst.k_dscnt
                fcost = cost * life_time_accepts * discount
                fcost = int(fcost)
                keyboard = kb.employerschoosebuy_1(fcost, life_time_accept)
                await message.answer(f'Стоимость размещения объявления: {fcost}. Списать средства и перейти к созданию?', reply_markup=keyboard)
            else:
                await message.answer("Неудалось загрузить цены, обратитесь в поддержку или повторите запрос")
    except Exception as e:
        await message.answer(f"Ошибка запроса, попробуйте еще раз. Код ошибки: {e} Повторить запрос?", reply_markup=keyboard)

#Обработка создания объяления в БД
@router.callback_query(F.data.startswith("empl_view_value_buy_"))
async def empl_view_value_buy(callback: CallbackQuery, state: FSMContext):
    fcost = int(callback.data.split("_")[4])
    user_id = callback.from_user.id
    posting_text = " "
    view_counter = 0
    accept_counter = 0
    rejected_counter = 0
    life_time_accept = int(callback.data.split("_")[5])
    active = 0
    costs = 0

    try:
        async with async_session() as session:
            result = await session.get(Employer, user_id)
            if result is None:
                await callback.message.answer("Пользователь не найден.")
                return

            cash = result.cash
            cash = int(cash)
            if cash >= fcost:
                stmt = update(Employer).where(Employer.user_id == user_id).values(cash=Employer.cash-fcost)
                await session.execute(stmt)
                cena = fcost
                new_posting = Postings(
                    user_id=user_id,
                    posting_text=posting_text,
                    view_counter=view_counter,
                    accept_counter=accept_counter,
                    rejected_counter=rejected_counter,
                    life_time_accept=life_time_accept,
                    life_time_date=None,
                    cost=costs,
                    active=active,
                    cena=cena
                    )
                session.add(new_posting)
                await session.flush()
                await session.refresh(new_posting)
                new_posting_id = new_posting.posting_id

                stmts = update(Postings).where(Postings.posting_id == new_posting_id).values(life_time_accept=life_time_accept)
                await session.execute(stmts)
                await session.commit()
                await callback.message.answer("Оплата прошла успешно, вы можете преступить к созданию объявления", reply_markup=kb.empl_goto_posting_accept)
                await state.set_state(posting_id_accept.posting_id)
                await state.update_data(posting_id=new_posting_id)
            else:
                await callback.message.answer("Недостаточно средств, поплнить счёт?", reply_markup=kb.empl_goto_cash)

    except Exception as e:
        keyboard = kb.employerschoosebuy_1(fcost, life_time_accept)
        await callback.message.answer(f"Ошибка запроса, попробуйте еще раз. Код ошибки: {e} Повторить запрос?", reply_markup=keyboard)
#Ввод текста объявления по количеству принятых
@router.callback_query(F.data.startswith("create_posting_accept_"))
async def create_posting_accept(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        posting_id = int(data["posting_id"])
        await state.set_state(posting_id_accept.posting_text)
    except (KeyError, ValueError):
        posting_id = int(callback.data.split("_")[3])
        await state.update_data(posting_id=posting_id)
        await state.set_state(posting_id_accept.posting_text)
    await callback.message.answer(f"Вот ваш номер объявления:{posting_id}")
    await callback.message.answer("Создание объявления, повторная инструкция и просьба отправить в чат текст объявления")

#Передача объявления на модерацию
@router.message(posting_id_accept.posting_text)
async def create_posting_accept_two(message: Message, state: FSMContext, bot: Bot):
    try:
        posting_text = message.text
        await state.update_data(posting_text=posting_text)
        data = await state.get_data()
        posting_id = int(data["posting_id"])
        posting_texts = str(data["posting_text"])
        user_id = int(message.from_user.id)
        async with async_session() as session:
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(posting_text=posting_texts)
            await session.execute(stmt)
            await session.commit()
        keyboard = kb.empl_publication_accept(posting_id)
        await bot.send_message(chat_id=user_id, text=f'Объявление переданно на модерацию. Текст объявления: {data["posting_text"]}')
        await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=
                             f'Пользователь: {user_id}, ссылка: tg://user?id={user_id} создал объявление, принять его к публикации?. Текст объявления: {data["posting_text"]}',
                             reply_markup=keyboard)
        await state.clear()
    except Exception as e:
        await bot.send_message(message.chat.id, f"Возникла непредвиденная ошибка. Код ошибки: {e}", reply_markup=kb.empl_goto_posting_accept)
        await state.clear()

#Команда для админа: опубликовать без изменений
@router.callback_query(F.data.startswith("publication_posting_accept_"), AdminC())
async def publication_posting_accept(callback: CallbackQuery, bot: Bot):
    posting_id = int(callback.data.split("_")[3])
    async with async_session() as session:
        try:
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(active=1)
            await session.execute(stmt)
            await session.commit()
            result = await session.get(Postings, posting_id)
            if result is None:
                await callback.message.answer("Объявление не найдено.")
                return
            user_id = int(result.user_id)
            await callback.message.answer(
                         f"Объявление успешно опубликовано, Время жизни: {result.life_time_accept}. Текст объявления:{result.posting_text}")
            await bot.send_message(chat_id=user_id, text=f"Объявление успешно опубликовано, Время жизни: {result.life_time_accept}. Текст объявления:{result.posting_text}")
        except Exception as e:
            keyboard = kb.empl_publication_accept(posting_id)
            await callback.message.answer(f"Произошла ошибка при публикации. Код ошибки: {e}", reply_markup=keyboard)

#Команда для админа: не публиковать, удалить из БД
@router.callback_query(F.data.startswith("delete_posting_accept_"), AdminC())
async def delete_posting_accept(callback: CallbackQuery, bot: Bot):
    posting_id = int(callback.data.split("_")[3])
    try:
        async with async_session() as session:

            result = await session.get(Postings, posting_id)
            if result is None:
                await callback.message.answer("Объявление не найдено.")
                return
            cost = int(result.cena)
            user_id = int(result.user_id)
            pst_id = int(result.posting_id)
            await delete_post(pst_id)
            stmt = update(Employer).where(Employer.user_id == user_id).values(cash=Employer.cash+cost)
            await session.execute(stmt)
            empl = await session.get(Employer, user_id)
            if empl is None:
                await callback.message.answer("Пользователь не найден, но объявления удалено.")
                return
            await session.execute(stmt)
            await session.commit()
        keyboardss = kb.employer_choose_posting_cost
        await callback.message.answer('Объявление успешно удалено из БД')
        await bot.send_message(chat_id=user_id, text=f'Объявление отклонено, средства начислены на ваш счёт. Баланс: {empl.cash}.', reply_markup=keyboardss)
    except Exception as e:
        keyboard = kb.empl_publication_accept(posting_id)
        await callback.message.answer(f"Произошла ошибка при публикации. Код ошибки: {e}", reply_markup=keyboard)

#Команда для админа: редактировать и опубликовать
@router.callback_query(F.data.startswith("edit_posting_accept_"), AdminC())
async def edit_posting_accept(callback: CallbackQuery, state: FSMContext):
    posting_id = int(callback.data.split('_')[3])
    await state.update_data(posting_id=posting_id)
    await state.set_state(posting_accept_text.npt)
    await callback.message.answer('Введите новый текст объявления')

@router.message(posting_accept_text.npt, AdminC())
async def edit_posting_accept_two(message: Message, state: FSMContext, bot: Bot):
    new_posting_text = message.text
    await state.update_data(npt=new_posting_text)
    data = await state.get_data()
    posting_id = int(data['posting_id'])
    posting_text = str(data['npt'])
    try:
        async with async_session() as session:
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(posting_text=posting_text, active=1)
            await session.execute(stmt)
            await session.commit()
            result = await session.get(Postings, posting_id)
            user_id = int(result.user_id)
            await bot.send_message(chat_id=user_id, text=f'Объявление успешно опубликовано. Текст был изменён на: {result.posting_text}, Количество откликов на объявление: {result.life_time_accept}')
            await message.answer(f'Объявление успешно опубликовано. Текст: {result.posting_text}')
        await state.clear()

    except Exception as e:
        await message.answer( f"Возникла непредвиденная ошибка. Код ошибки: {e}")
        await state.clear()
        return
#Конец обработки создания объявления по количеству принятых

#Начало обработки создания объявления по дате
# Обработка команды подтверждения выбора/по количеству принятых
@router.callback_query(F.data == 'empl_time_value')
async def empl_view_value(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вы выбрали продукт ограниченный по времени? Введите количество недель, которые хотите приобрести")

    await state.set_state(date_accept_cost.weeks)


# Обработка покупки и создания объявления по дате
@router.message(date_accept_cost.weeks)
async def dac(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректное число. Например: 3 или 777")
        return
    weeks = message.text
    await state.update_data(weeks=weeks)
    data = await state.get_data()
    weeks = int(data["weeks"])
    await state.clear()
    try:
        async with async_session() as session:
            cst = await session.execute(select(Support))
            ccst = cst.scalars().first()
            if ccst:
                cost = ccst.cost_week
                discount = ccst.k_dscnt
                fcost = cost * weeks * discount
                fcost = int(fcost)
                keyboard = kb.employerschoosebuy_2(fcost, weeks)
                await message.answer(
                    f'Стоимость размещения объявления: {fcost}. Списать средства и перейти к созданию?',
                    reply_markup=keyboard)
            else:
                await message.answer("Неудалось загрузить цены, обратитесь в поддержку или повторите запрос")
    except Exception as e:
        await message.answer(f"Ошибка запроса, попробуйте еще раз. Код ошибки: {e} Повторить запрос?",
                             reply_markup=keyboard)


# Обработка создания объяления в БД
@router.callback_query(F.data.startswith("empl_date_value_buy_"))
async def empl_date_value_buy(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    if len(parts) < 6:
        await callback.message.answer("Некорректный формат данных. Повторите попытку.")
        return
    fcost = int(callback.data.split("_")[4])
    user_id = callback.from_user.id
    posting_text = " "
    view_counter = 0
    accept_counter = 0
    rejected_counter = 0
    weeks = int(callback.data.split("_")[5])
    active = 0
    costs = 0

    try:
        async with async_session() as session:
            result = await session.get(Employer, user_id)
            if result is None:
                await callback.message.answer("Пользователь не найден.")
                return

            cash = result.cash
            cash = int(cash)
            current_date = date.today()
            new_date = current_date + relativedelta(weeks=weeks)
            if cash >= fcost:
                stmt = update(Employer).where(Employer.user_id == user_id).values(cash=Employer.cash - fcost)
                await session.execute(stmt)
                cena = fcost
                new_posting = Postings(
                    user_id=user_id,
                    posting_text=posting_text,
                    view_counter=view_counter,
                    accept_counter=accept_counter,
                    rejected_counter=rejected_counter,
                    life_time_accept=0,
                    life_time_date=new_date,
                    cost=costs,
                    active=active,
                    cena=cena
                )
                session.add(new_posting)
                await session.flush()
                await session.refresh(new_posting)
                new_posting_id = new_posting.posting_id
                await session.commit()
                await callback.message.answer("Оплата прошла успешно, вы можете преступить к созданию объявления",
                                              reply_markup=kb.empl_goto_posting_date)
                await state.set_state(posting_id_date.posting_id)
                await state.update_data(posting_id=new_posting_id)
            else:
                await callback.message.answer("Недостаточно средств, поплнить счёт?", reply_markup=kb.empl_goto_cash)

    except Exception as e:
        keyboard = kb.employerschoosebuy_2(fcost, weeks)
        await callback.message.answer(f"Ошибка запроса, попробуйте еще раз. Код ошибки: {e} Повторить запрос?",
                                      reply_markup=keyboard)


# Ввод текста объявления по дате
@router.callback_query(F.data.startswith("create_posting_date_"))
async def create_posting_date(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        posting_id = int(data["posting_id"])
        await state.set_state(posting_id_date.posting_text)
    except (KeyError, ValueError):
        posting_id = int(callback.data.split("_")[3])
        await state.update_data(posting_id=posting_id)
        await state.set_state(posting_id_date.posting_text)
    await callback.message.answer(f"Вот ваш номер объявления:{posting_id}")
    await callback.message.answer(
        "Создание объявления, повторная инструкция и просьба отправить в чат текст объявления")


# Передача объявления на модерацию
@router.message(posting_id_date.posting_text)
async def create_posting_date_two(message: Message, state: FSMContext, bot: Bot):
    try:
        posting_text = message.text
        await state.update_data(posting_text=posting_text)
        data = await state.get_data()
        posting_id = int(data["posting_id"])
        posting_texts = str(data["posting_text"])
        user_id = int(message.from_user.id)
        async with async_session() as session:
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(posting_text=posting_texts)
            await session.execute(stmt)
            await session.commit()
        keyboard = kb.empl_publication_date(posting_id)
        await bot.send_message(chat_id=user_id,
                               text=f'Объявление переданно на модерацию. Текст объявления: {posting_texts}')
        await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=
        f'Пользователь: {user_id}, ссылка: tg://user?id={user_id} создал объявление, принять его к публикации?. Текст объявления: {data["posting_text"]}',
                               reply_markup=keyboard)
        await state.clear()
    except Exception as e:
        await bot.send_message(message.chat.id, f"Возникла непредвиденная ошибка. Код ошибки: {e}",
                               reply_markup=kb.empl_goto_posting_accept)
        await state.clear()


# Команда для админа: опубликовать без изменений
@router.callback_query(F.data.startswith("publication_posting_date_"), AdminC())
async def publication_posting_date(callback: CallbackQuery, bot: Bot):
    posting_id = int(callback.data.split("_")[3])
    async with async_session() as session:
        try:
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(active=1)
            await session.execute(stmt)
            await session.commit()
            result = await session.get(Postings, posting_id)
            if result is None:
                await callback.message.answer("Объявление не найдено.")
                return
            user_id = int(result.user_id)
            await callback.message.answer(
                f"Объявление успешно опубликовано, Время жизни: {result.life_time_date}. Текст объявления:{result.posting_text}")
            await bot.send_message(chat_id=user_id,
                                   text=f"Объявление успешно опубликовано, Время жизни: {result.life_time_date}. Текст объявления:{result.posting_text}")
        except Exception as e:
            keyboard = kb.empl_publication_date(posting_id)
            await callback.message.answer(f"Произошла ошибка при публикации. Код ошибки: {e}", reply_markup=keyboard)


# Команда для админа: не публиковать, удалить из БД
@router.callback_query(F.data.startswith("delete_posting_date_"), AdminC())
async def delete_posting_accept(callback: CallbackQuery, bot: Bot):
    posting_id = int(callback.data.split("_")[3])
    try:
        async with async_session() as session:

            result = await session.get(Postings, posting_id)
            if result is None:
                await callback.message.answer("Объявление не найдено.")
                return
            cost = int(result.cena)
            user_id = int(result.user_id)
            pst_id = int(result.posting_id)
            await delete_post(pst_id)
            stmt = update(Employer).where(Employer.user_id == user_id).values(cash=Employer.cash + cost)
            await session.execute(stmt)
            empl = await session.get(Employer, user_id)
            if empl is None:
                await callback.message.answer("Пользователь не найден, но объявления удалено.")
                return
            await session.commit()
        keyboardss = kb.employer_choose_posting_cost
        await callback.message.answer('Объявление успешно удалено из БД')
        await bot.send_message(chat_id=user_id,
                               text=f'Объявление отклонено, средства начислены на ваш счёт. Баланс: {empl.cash}.',
                               reply_markup=keyboardss)
    except Exception as e:
        keyboard = kb.empl_publication_date(posting_id)
        await callback.message.answer(f"Произошла ошибка при публикации. Код ошибки: {e}", reply_markup=keyboard)


# Команда для админа: редактировать и опубликовать
@router.callback_query(F.data.startswith("edit_posting_date_"), AdminC())
async def edit_posting_date(callback: CallbackQuery, state: FSMContext):
    posting_id = int(callback.data.split('_')[3])
    await state.set_state(posting_date_text.npt)
    await state.update_data(posting_id=posting_id)
    await callback.message.answer('Введите новый текст объявления')


@router.message(posting_date_text.npt, AdminC())
async def edit_posting_date_two(message: Message, state: FSMContext, bot: Bot):
    new_posting_text = message.text
    await state.update_data(npt=new_posting_text)
    data = await state.get_data()
    posting_id = int(data['posting_id'])
    posting_text = str(data['npt'])
    try:
        async with async_session() as session:
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(posting_text=posting_text, active=1)
            await session.execute(stmt)
            await session.commit()
            result = await session.get(Postings, posting_id)
            user_id = int(result.user_id)
            await bot.send_message(chat_id=user_id,
                                   text=f'Объявление успешно опубликовано. Текст был изменён на: {result.posting_text}, Количество откликов на объявление: {result.life_time_date}')
            await message.answer(f'Объявление успешно опубликовано. Текст: {result.posting_text}')
        await state.clear()

    except Exception as e:
        await message.answer(f"Возникла непредвиденная ошибка. Код ошибки: {e}")
        await state.clear()
        return
#Конец обработки команды создания объявления по времени

#Команда личный кабинет
@router.message(Command("lk"))
async def empl_lk(message: Message):
    keyboard = kb.empl_lk
    await message.answer('Выберите функции личного кабинета', reply_markup=keyboard)

#Обработки команды обращения в поддержку
@router.callback_query(F.data == 'help')
async def help(callback: CallbackQuery):
    keyboard = kb.help()
    await callback.message.answer('Нажмите для перехода в чат поддрежки', reply_markup=keyboard)

#Начало обработки команды Продлить
@router.callback_query(F.data == 'prodlit')
async def prodlit(callback: CallbackQuery):
    await callback.message.answer('Выберите объявление которое хотите продлить')
    user_id = callback.from_user.id
    username = callback.from_user.username
    accept = False
    date_accept = False
    async with async_session() as session:
        try:
            print(f"[DEBUG] user_id in callback: {user_id}")
            print(f"User ID: {user_id}, Username: {username}")
            stmt = select(Postings).where(Postings.user_id == user_id)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            if not rows:
                user = await session.get(Employer, user_id)
                cash = int(user.cash)
                if cash > 0:
                    keyboard = kb.employer_choose_posting_cost
                    await callback.message.answer('Нет активных объявлений. Перейти к покупкам?', reply_markup=keyboard)
                else:
                    keyboards = kb.goto_choose_product
                    await callback.message.answer('Нет активных объявлений. Перейти к покупкам?', reply_markup=keyboards)
                return
        except Exception as e:
            await callback.message.answer(f"Ошибка при получении данных: {e}.")
            return

        try:
            stmt_accept = select(Postings).where(
                and_(Postings.user_id == user_id, Postings.life_time_accept > 0, Postings.active == 1))
            result = await session.execute(stmt_accept)
            rows = result.scalars().all()
            if rows:
                posting_ids = [row.posting_id for row in rows]
                await callback.message.answer('Выберите объявление которое хотите редактировать по количеству принятых',
                                     reply_markup=await kb.postings_id_c(posting_ids))
                accept = True
            stmt_date = select(Postings).where(
                and_(Postings.user_id == user_id, Postings.life_time_date.is_not(None), Postings.active == 1))
            result1 = await session.execute(stmt_date)
            rows1 = result1.scalars().all()
            if rows1:
                posting_idss = [row.posting_id for row in rows1]
                await callback.message.answer('Выберите объявление которое хотите редактировать по дате',
                                     reply_markup=await kb.postings_id_e(posting_idss))
                date_accept = True
            if not date_accept and not accept:
                await callback.message.answer('У вас нет активных объявлений которые можно отредактировать')
        except Exception as e:
            await callback.message.answer(f'Ошибка. Код ошибки: {e}')
            return

#Начало обработки команды Продлить объявление по дате
@router.callback_query(F.data.startswith("prodlit_posting_date_"))
async def prodlit_two(callback: CallbackQuery, state: FSMContext):
    try:
        posting_id = int(callback.data.split("_")[3])
        await state.set_state(prodlite.posting_value1)
        await state.update_data(posting_id1=posting_id)
        await callback.message.answer(
            "Укажите количество недель на которые хотите продлить объявление")
    except Exception as e:
        await callback.message.answer(f'Ошибка. Код ошибки: {e}')
        return

@router.message(prodlite.posting_value1)
async def prodlit_three(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректное число. Например: 3 или 777")
        return
    try:
        posting_value = int(message.text)
        await state.update_data(posting_value1=posting_value)
        data = await state.get_data()
        posting_id = int(data["posting_id1"])
        user_id = int(message.from_user.id)
        async with async_session() as session:
            user = await session.get(Employer, user_id)
            posting = await session.get(Postings, posting_id)
            cash = int(user.cash)
            cst = await session.execute(select(Support))
            ccst = cst.scalars().first()
            current_date = posting.life_time_date
            await state.update_data(current_date1=current_date)
            if not current_date:
                await message.answer('Невозможно продлить: дата окончания не установлена.')
                return
            if ccst:
                cost = ccst.cost_week
                discount = ccst.k_dscnt
                fcost = cost * posting_value * discount
                fcost = int(fcost)
                await state.update_data(fcost1=fcost)
                if cash >= fcost:
                    await message.answer(f'Стоимость продления: {fcost}. Продливаем?', reply_markup=kb.prodlit_date)
                else:
                    await message.answer('Недостаточно средств для продления, пополнить', reply_markup=kb.empl_goto_cash)
            else:
                await message.answer('Ошибка получения данных, попробуйте поже')
    except Exception as e:
        await bot.send_message(message.chat.id, f"Возникла непредвиденная ошибка. Код ошибки: {e}",)
        await state.clear()

@router.callback_query(F.data.startswith("prodlit_date_two"))
async def prodlit_three_2(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        posting_id = int(data["posting_id1"])
        user_id = callback.from_user.id
        fcost = int(data["fcost1"])
        posting_value = int(data["posting_value1"])
        current_date = data["current_date1"]
        async with async_session() as session:
            new_date = current_date + relativedelta(weeks=posting_value)
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(life_time_date=new_date)
            await session.execute(stmt)
            stmt1 = update(Employer).where(Employer.user_id == user_id).values(cash=Employer.cash - fcost)
            await session.execute(stmt1)
            user2 = await session.get(Employer, user_id)
            await bot.send_message(chat_id=user_id,
                                   text=f'Объявление успешно продлено на {posting_value} недель. Ваш баланс был изменен на: {int(user2.cash)}')
            await session.commit()
        await state.clear()
    except Exception as e:
        await bot.send_message(callback.message.chat.id, f"Возникла непредвиденная ошибка. Код ошибки: {e}",)
        await state.clear()
#Конец обработки команды Продлить объявление по дате


#Начало обработки команды Продлить объявление по количеству принятых
@router.callback_query(F.data.startswith("prodlit_posting_accept_"))
async def prodlit_four(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        posting_id = int(callback.data.split("_")[3])
        await state.set_state(prodlit1.posting_value)
        await state.update_data(posting_id=posting_id)
        await callback.message.answer(
            "Укажите количество откликов на которые хотите продлить объявление")
    except Exception as e:
        await bot.send_message(chat_id=callback.from_user.id, text=f'Ошибка. Код ошибки: {e}')
        return


@router.message(prodlit1.posting_value)
async def prodlit_five(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректное число. Например: 3 или 777")
        return
    try:
        posting_value = int(message.text)
        await state.update_data(posting_value=posting_value)
        data = await state.get_data()
        posting_id = int(data["posting_id"])
        user_id = int(message.from_user.id)
        async with async_session() as session:
            user = await session.get(Employer, user_id)
            posting = await session.get(Postings, posting_id)
            if not user or not posting:
                await message.answer("Ошибка: не удалось найти данные пользователя или объявления.")
                return
            cash = int(user.cash)
            cst = await session.execute(select(Support))
            ccst = cst.scalars().first()
            current_life = int(posting.life_time_accept)
            if ccst:
                cost = ccst.cost_view
                discount = ccst.k_dscnt
                fcost = int(cost * posting_value * discount)
                await state.update_data(fcost=fcost)
                if cash >= fcost:
                    new_lft = current_life+posting_value
                    await state.update_data(current_date=new_lft)
                    await message.answer(f'Продление стоит: {fcost} откликов. Продливаем?', reply_markup=kb.prodlit_accept)
                else:
                    await message.answer('Недостаточно средств для продления, пополнить',
                                         reply_markup=kb.empl_goto_cash)
            else:
                await message.answer('Ошибка получения данных, попробуйте поже')
    except Exception as e:
        await bot.send_message(message.chat.id, f"Возникла непредвиденная ошибка. Код ошибки: {e}")
        await state.clear()

@router.callback_query(F.data.startswith("prodlit_accept_two"))
async def prodlit_five_2(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        user_id = callback.from_user.id
        data = await state.get_data()
        posting_id = int(data["posting_id"])
        fcost = int(data["fcost"])
        posting_value = int(data["posting_value"])
        new_lft = int(data["current_date"])
        async with async_session() as session:
            stmt = update(Postings).where(Postings.posting_id == posting_id).values(life_time_accept=new_lft)
            await session.execute(stmt)
            stmt1 = update(Employer).where(Employer.user_id == user_id).values(cash=Employer.cash - fcost)
            await session.execute(stmt1)
            user2 = await session.get(Employer, user_id)
            await bot.send_message(chat_id=user_id,
                                   text=f'Объявление успешно продлено на {posting_value} откликов. Ваш баланс был изменен на: {int(user2.cash)}')
            await session.commit()
            await state.clear()
    except Exception as e:
        await bot.send_message(callback.message.chat.id, f"Возникла непредвиденная ошибка. Код ошибки: {e}",)
        await state.clear()
#Конец обработки команды Продлить объявление по количеству принятых
#Конец обработки команды Продлить

#Начало обработки команды Инфо
@router.callback_query(F.data == 'postings_info')
async def postings_info(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    try:
        async with async_session() as session:
            stmt = select(Postings).where(Postings.user_id == user_id)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            if not rows:
                await callback.message.answer('У вас пока не было обявлений')
                return
            message_text = []
            for row in rows:
                if row.active == 1:
                   active = str('Да')
                else:
                    active = str('Нет')

                if row.life_time_accept > 0 and row.life_time_date == None:
                    message_text.extend([f'ID объявления: {row.posting_id}', f'Текст объявления: "{row.posting_text}"',
                                         f'Просмотрено: {row.view_counter}', f'Принято: {row.accept_counter}', f'Время жизни: {row.life_time_accept}',
                                         f'Создано: {row.created_at}', f'Активно?: {active}'])
                else:
                    message_text.extend([f'ID объявления: {row.posting_id}', f'Текст объявления: "{row.posting_text}"',
                                         f'Просмотрено: {row.view_counter}', f'Принято: {row.accept_counter}',
                                         f'Время жизни: {row.life_time_date}',
                                         f'Создано: {row.created_at}', f'Активно?: {active}'])
            await callback.message.answer("\n\n".join(message_text))
    except Exception as e:
        await bot.send_message(chat_id=callback.message.chat.id, text=f"Возникла непредвиденная ошибка. Код ошибки: {e}")
