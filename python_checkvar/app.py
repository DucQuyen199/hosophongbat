from flask import Flask, render_template, request
from flask_caching import Cache
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456aA@$',
        database='checkvar'
    )

@app.route('/')
@cache.cached(timeout=60, query_string=True)
def index():
    search_query = request.args.get('search', '')
    if not search_query:
        # Không có từ khóa tìm kiếm, không trả về dữ liệu
        return render_template('index.html', transactions=[], page=1, total_pages=0, search_query='')

    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    try:
        connection = get_db_connection()
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT * FROM transactions WHERE description LIKE %s LIMIT %s OFFSET %s',
                ('%' + search_query + '%', per_page, offset)
            )
            transactions = cursor.fetchall()

        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) FROM transactions WHERE description LIKE %s',
                ('%' + search_query + '%',)
            )
            total_records = cursor.fetchone()[0]
            total_pages = (total_records + per_page - 1) // per_page

    except Error as e:
        print(f"Error: {e}")
        transactions = []
        total_pages = 0

    finally:
        connection.close()

    return render_template('index.html', transactions=transactions, page=page, total_pages=total_pages, search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True)
