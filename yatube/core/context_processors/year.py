import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    dt = datetime.datetime.now()
    year_now = int(dt.strftime('%Y'))
    return {
        'year': year_now
    }
