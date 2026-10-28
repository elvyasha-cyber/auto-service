-- Десять тестовых заявок для очереди.
-- Температуры в таблице нет: её считает программа по полям.
-- Повторный запуск не создаёт дубли: у каждого человека свой телефон.

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Игорь', 'Семёнов', 'Петрович',
    'Личная машина, езжу на работу.',
    'от 12 000 ₽ до 18 000 ₽',
    'Телефон',
    '+7 900 100-00-01', 'igor@example.com', '', '', '',
    'Машина встала на дороге, до работы не доехал.',
    'частный автомобиль', '1 человек', 'один автомобиль', 'Сотрудник', 'личная машина',
    'один раз', 'сегодня, машина не едет', 'разовая работа', 'эвакуация и запуск', 'сейчас'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-01');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Марина', 'Волкова', 'Сергеевна',
    'Один автомобиль для себя, решение принимаю сама.',
    'от 450 000 ₽ до 700 000 ₽',
    'Телефон, почта',
    '+7 900 100-00-02', 'marina@example.com', '', '', '',
    'Нужны детейлинг и керамика на один кузов.',
    'частная коллекция', '6 человек', 'один автомобиль', 'Руководитель', 'одна мастерская',
    'один кузов', 'в следующем квартале', 'разовая работа', 'керамика кузова', 'будни с 11 до 16'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-02');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Павел', 'Орлов', 'Ильич',
    'Возим продукты по городу, машины работают каждый день.',
    'от 40 000 ₽ до 70 000 ₽',
    'Телефон, Telegram',
    '+7 900 100-00-03', '', '@pavel_orlov_test', '', '',
    'Нужно посмотреть подвеску у части машин, список пришлю.',
    'логистика и доставка', '4 человека', 'автопарк 28 машин', 'Сотрудник', 'один офис',
    'список пришлём отдельно', 'к концу месяца', 'разовая работа', 'ремонт подвески', 'после 19:00'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-03');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Елена', 'Крылова', 'Андреевна',
    'Сеть кофеен, у каждой точки служебная машина.',
    'от 60 000 ₽ до 90 000 ₽',
    'Телефон, почта, WhatsApp',
    '+7 900 100-00-04', 'elena@example.com', '', '+7 900 100-00-04', '',
    'Хотим плановые заезды, спешки нет.',
    'сеть кофеен', '120 человек', 'по одной машине на филиал', 'Сотрудник', 'сеть из 6 филиалов',
    'осмотр точек раз в квартал', 'к лету, можно планировать', 'постоянное сопровождение',
    'договорное обслуживание', 'понедельник, первая половина дня'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-04');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Андрей', 'Белов', 'Олегович',
    'Шиномонтаж у дома, одна рабочая машина.',
    'от 35 000 ₽ до 55 000 ₽',
    'Телефон',
    '+7 900 100-00-05', '', '', '', '',
    'Скрипят колодки, могу подождать.',
    'шиномонтаж', '8 человек', 'один автомобиль', 'Руководитель', 'одна точка',
    'одна машина', 'через две недели', 'разовая работа', 'замена колодок', 'суббота утром'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-05');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Ольга', 'Никитина', 'Игоревна',
    'Небольшое такси, три машины на линии.',
    'от 15 000 ₽ до 22 000 ₽',
    'Telegram',
    '+7 900 100-00-06', '', '@olga_taxi_test', '', '',
    'Как появится окно, пригоним по одной.',
    'частное такси', '5 человек', '3 машины', 'Сотрудник', 'одна диспетчерская',
    'по одной, когда освободится бокс', 'в течение месяца, без конкретной даты', 'разовая работа',
    'диагностика', 'любой будний день'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-06');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Сергей', 'Ким', 'Павлович',
    'Личный седан, дату могу сдвинуть.',
    'от 90 000 ₽ до 140 000 ₽',
    'Почта',
    '+7 900 100-00-07', 'sergey@example.com', '', '', '',
    'Бюджет есть, дата гибкая.',
    'для себя', '2 человека', 'один автомобиль', 'Сотрудник', 'личный автомобиль',
    'один заезд', 'когда будет удобно мастеру', 'разовая работа', 'комплекс на седан', 'после 18:00'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-07');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Дарья', 'Морозова', 'Алексеевна',
    'Пока сравниваю цены, машину не записывала.',
    'от 3 000 ₽ до 7 000 ₽',
    'Телефон',
    '+7 900 100-00-08', '', '', '', '',
    'Пока только узнаю цену.',
    'для себя', 'я одна', 'один автомобиль', 'Сотрудник', 'личная машина',
    'не решила', 'не срочно, просто прицениваюсь', 'консультация', 'консультация по цене', 'не важно'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-08');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Никита', 'Соловьёв', '',
    'Собираю хобби-проект в гараже.',
    'от 5 000 ₽ до 9 000 ₽',
    'Макс',
    '+7 900 100-00-09', '', '', '', 'Никита Соловьёв',
    'К работе не привязан, смотрю на будущее.',
    'хобби', '', 'одна деталь', '', 'гараж',
    'одна деталь', 'в следующем году, если останутся деньги', 'посмотреть', 'заказ редкой детали', 'напишите в Макс'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-09');

INSERT INTO leads (
    first_name, last_name, middle_name, business_info, budget, contact_method,
    phone, email, telegram, whatsapp, max_contact, comment,
    business_niche, company_size, task_volume, client_role, business_size,
    need_volume, deadline, task_type, product, convenient_time
)
SELECT
    'Ирина', 'Павлова', '',
    'Частное лицо, одна небольшая царапина.',
    'от 8 000 ₽ до 12 000 ₽',
    'WhatsApp',
    '+7 900 100-00-10', '', '', '+7 900 100-00-10', '',
    'Маленький скол на двери.',
    'частное лицо', '1 человек', 'одна машина', 'Сотрудник', 'личная машина',
    'один скол', 'не горит', 'разовая мелочь', 'подкраска скола', 'днём'
WHERE NOT EXISTS (SELECT 1 FROM leads WHERE phone = '+7 900 100-00-10');
