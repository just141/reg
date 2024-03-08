from flask import Flask, render_template, request, json
import sqlite3
from datetime import datetime
import hashlib



app = Flask(__name__)


@app.route('/users')
@app.route('/')
def users_view():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id, login, role, date FROM Users')
    users = cursor.fetchall()

    return render_template('users.html', data=users)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    login = request.form.get('login')
    password = hashlib.md5(request.form.get('password').encode()).hexdigest()
    role = request.form.get('role')
    date = '{}.{}.{}'.format(datetime.now().day,
                            datetime.now().month,
                            datetime.now().year)

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    test = cursor.execute('SELECT login FROM Users WHERE login = ?', (login, )).fetchall()
    if test == []:
        cursor.execute('''
                INSERT INTO Users (login, password, role, date) 
                VALUES (?, ?, ?, ?)''',
                (login, password, role, date))

        connection.commit()
        cursor.execute('SELECT id FROM Users WHERE login = ?', (login, ))
        new_user = cursor.fetchall()
        connection.close()

        return json.dumps({'id':new_user[0][0],
                        'login':login,
                        'role':role,
                        'date':date,
                        'result':1})
    else:
        return json.dumps({'result':2})


@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    id = request.form.get('id')
    login = request.form.get('login')
    password = hashlib.md5(request.form.get('password').encode()).hexdigest()
    role = request.form.get('role')

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    for i in ['login', 'password', 'role']:
        if eval(i) != '':
            if i == 'login':
                test = cursor.execute('SELECT login FROM Users WHERE login = ? AND id <> ?', (login, id)).fetchall()
                if test == []:
                    cursor.execute(f'UPDATE Users SET {i} = ? WHERE id = ?',
                                    (eval(i), id))
                    connection.commit()
                else:
                    return json.dumps({'result':2})
            else:
                cursor.execute(f'UPDATE Users SET {i} = ? WHERE id = ?',
                                    (eval(i), id))
                connection.commit()
    
    connection.close()

    return json.dumps({'login':login,
                       'role':role, 
                       'result':1})


@app.route('/del_user', methods=['GET', 'POST'])
def del_user():
    id = request.form.get('id')
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Users WHERE id = ?', (id,))
    connection.commit()
    connection.close()

    return json.dumps({'del_user':'good'})



if __name__ == '__main__':
    app.run(debug=True)



