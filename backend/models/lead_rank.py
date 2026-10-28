import re

HOT = "горячая"
WARM = "тёплая"
COLD = "холодная"


def _plain(*parts) -> str:
    text = " ".join(str(part or "") for part in parts).lower().replace("ё", "е")
    return re.sub(r"\s+", " ", text).strip()


def _numbers(text: str) -> list[int]:
    compact = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
    return [int(item) for item in re.findall(r"\d+", compact)]


def _budget_middle(budget: str) -> float:
    numbers = _numbers(budget)
    if not numbers:
        return 0
    if len(numbers) >= 2:
        return (numbers[0] + numbers[-1]) / 2
    return numbers[0]


def _full_name(lead: dict) -> str:
    parts = [lead.get("last_name"), lead.get("first_name"), lead.get("middle_name")]
    name = " ".join(str(part).strip() for part in parts if str(part or "").strip())
    return name or "Без имени"


def rank_lead(lead: dict) -> dict:
    """Температура заявки по полям. Отдельного статуса «срочно» в базе нет."""
    marks: list[tuple[int, str]] = []

    deadline = _plain(lead.get("deadline"))
    cold_deadline = any(
        word in deadline
        for word in (
            "не сроч",
            "не горит",
            "когда-нибудь",
            "когда нибудь",
            "следующем году",
            "следующий год",
            "не важно",
            "прицен",
        )
    )
    if cold_deadline:
        marks.append((0, "срок не горит"))
    elif any(word in deadline for word in ("сегодня", "сейчас", "срочно", "не едет", "в течение дня", "до конца дня")):
        marks.append((44, "результат нужен сегодня"))
    elif "завтра" in deadline:
        marks.append((34, "результат нужен завтра"))
    elif any(word in deadline for word in ("на этой неделе", "пару дней", "два дня", "три дня", "2 дня", "3 дня")):
        marks.append((24, "срок — эта неделя"))
    elif any(word in deadline for word in ("две недели", "в этом месяце", "к концу месяца", "до конца месяца", "через месяц")):
        marks.append((12, "срок в пределах месяца"))
    elif deadline:
        marks.append((6, "срок назван, но без спешки"))
    else:
        marks.append((0, "срок не указан"))

    budget = _budget_middle(_plain(lead.get("budget")))
    if budget >= 300_000:
        marks.append((30, "бюджет крупный"))
    elif budget >= 80_000:
        marks.append((18, "бюджет заметный"))
    elif budget >= 25_000:
        marks.append((8, "бюджет обычный"))
    elif budget > 0:
        marks.append((2, "бюджет небольшой"))

    role = _plain(lead.get("client_role"))
    leader = any(word in role for word in ("руковод", "владел", "директор", "собствен"))
    if leader:
        marks.append((18, "заявку оставил тот, кто принимает решение"))
    elif "сотруд" in role:
        marks.append((4, "заявку оставил сотрудник"))

    size_text = _plain(lead.get("company_size"), lead.get("business_size"))
    size_numbers = _numbers(size_text)
    size = max(size_numbers) if size_numbers else 0
    large = size >= 40 or any(word in size_text for word in ("филиал", "сеть", "крупн", "холдинг"))
    if large:
        marks.append((22, "компания крупная"))
    elif size >= 10:
        marks.append((10, "компания небольшая"))

    volume_text = _plain(lead.get("task_volume"), lead.get("need_volume"))
    volume_numbers = _numbers(volume_text)
    volume = max(volume_numbers) if volume_numbers else 0
    fleet = volume >= 15 or any(
        word in volume_text
        for word in ("парк", "автопарк", "парти", "флот", "ежемесяч", "каждую неделю", "регуляр", "абонент")
    )
    if fleet:
        marks.append((24, "большой или регулярный объём"))
    elif volume >= 3 or any(word in volume_text for word in ("несколько", "пара машин", "две машин", "три машин")):
        marks.append((10, "несколько машин"))

    niche = _plain(lead.get("business_niche"), lead.get("business_info"))
    corporate_niche = any(
        word in niche
        for word in ("логист", "такси", "каршеринг", "автопарк", "дилер", "перевоз", "доставк", "корпоратив")
    )
    if corporate_niche:
        marks.append((16, "ниша — транспорт или корпоративный клиент"))

    task = _plain(lead.get("task_type"))
    contract = any(word in task for word in ("сопровожд", "договор", "абонент", "постоян"))
    if contract:
        marks.append((16, "нужно постоянное сопровождение"))

    score = sum(points for points, _text in marks)
    if score >= 48:
        temperature = HOT
    elif score >= 22:
        temperature = WARM
    else:
        temperature = COLD

    positive = [text for points, text in sorted(marks, key=lambda item: item[0], reverse=True) if points > 0]
    quiet = [text for points, text in marks if points == 0]
    reasons = (quiet + positive) if temperature == COLD else positive
    if not reasons:
        reasons = ["мало признаков, что заявка срочная"]

    urgent = (not cold_deadline) and any(
        word in deadline for word in ("сегодня", "завтра", "срочно", "не едет", "в течение дня", "до конца дня")
    )
    if contract and large:
        department = "Договорное сопровождение"
    elif fleet or large:
        department = "Корпоративный отдел"
    elif urgent and temperature == HOT:
        department = "Срочная приёмка"
    elif budget >= 300_000:
        department = "Персональный приём"
    elif temperature == COLD:
        department = "Общая очередь"
    else:
        department = "Мастерская"

    manager = bool(budget >= 300_000 or large or contract or fleet or (leader and budget >= 80_000))
    if temperature == HOT:
        spend = "Да. Ответить в первую очередь."
    elif temperature == WARM:
        spend = "Да, но после горячих. Обычная очередь мастерской."
    else:
        spend = "Не в приоритете. Можно ответить, когда освободитесь."

    return {
        **lead,
        "full_name": _full_name(lead),
        "score": score,
        "temperature": temperature,
        "main_reason": reasons[0],
        "reasons": reasons,
        "department": department,
        "personal_manager": manager,
        "manager_text": (
            "Нужен персональный менеджер."
            if manager
            else "Персональный менеджер не нужен."
        ),
        "spend_time": spend,
    }


def rank_queue(rows: list[dict]) -> dict:
    items = [rank_lead(row) for row in rows]
    order = {HOT: 0, WARM: 1, COLD: 2}
    items.sort(key=lambda item: (order[item["temperature"]], -item["score"], item.get("id") or 0))
    for place, item in enumerate(items, start=1):
        item["place"] = place
    return {
        "total": len(items),
        "hot": sum(item["temperature"] == HOT for item in items),
        "warm": sum(item["temperature"] == WARM for item in items),
        "cold": sum(item["temperature"] == COLD for item in items),
        "with_manager": sum(bool(item["personal_manager"]) for item in items),
        "items": items,
    }
