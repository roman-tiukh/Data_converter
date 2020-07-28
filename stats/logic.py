from datetime import datetime
from django.db import connection


def get_api_usage_by_day(date_from: datetime, date_to: datetime,
                         user_id: int) -> [dict]:
    days = []
    with connection.cursor() as c:
        c.execute(f"""
            SELECT date(max("timestamp")), count(*) as count
            FROM stats_api_usage_tracking
            WHERE "timestamp" >= %(date_from)s AND "timestamp" <= %(date_to)s
                AND user_id = %(user_id)s
            GROUP BY date_part('doy', "timestamp")
            ORDER BY max("timestamp")
        """, {
            'date_from': date_from,
            'date_to': date_to,
            'user_id': user_id
        })
        for row in c.fetchall():
            days.append({
                'timestamp': row[0],
                'count': row[1],
            })
    return days
