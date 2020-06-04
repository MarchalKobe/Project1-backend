from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens


    @staticmethod
    def read_value_sensor(sensorid, date):
        date = f"{date}%"
        sql = "SELECT Datum, Waarde FROM Historiek WHERE ApparaatID = %s AND Datum LIKE %s ORDER BY Datum"
        params = [sensorid, date]
        return Database.get_rows(sql, params)
    

    @staticmethod
    def add_value_sensor(sensorid, data):
        sql = "INSERT INTO Historiek (ApparaatID, Waarde) VALUES (%s, %s)"
        params = [sensorid, data]
        return Database.execute_sql(sql, params)
    

    @staticmethod
    def get_password_by_user(username):
        sql = "SELECT Wachtwoord FROM Gebruikers WHERE Naam = %s"
        params = [username]
        return Database.get_one_row(sql, params)
    

    @staticmethod
    def read_activiteiten_days(date):
        date = f"{date}%"
        sql = "SELECT Datum FROM Activiteiten WHERE Datum LIKE %s ORDER BY Datum"
        params = [date]
        return Database.get_rows(sql, params)
    

    @staticmethod
    def read_activiteiten(date):
        date = f"{date}%"
        sql = "SELECT ActiviteitID, Datum, Activiteit, LinkID FROM Activiteiten WHERE Datum LIKE %s ORDER BY Datum"
        params = [date]
        return Database.get_rows(sql, params)
    

    @staticmethod
    def get_activiteiten_link(id):
        sql = "SELECT LinkID FROM Activiteiten WHERE ActiviteitID = %s"
        params = [id]
        return Database.get_one_row(sql, params)
    

    @staticmethod
    def update_activiteit(id, event, date):
        sql = "UPDATE Activiteiten SET Activiteit = %s, Datum = %s WHERE ActiviteitID = %s"
        params = [event, date, id]
        return Database.execute_sql(sql, params)
    

    @staticmethod
    def delete_activiteit(id):
        sql = "DELETE FROM Activiteiten WHERE ActiviteitID = %s"
        params = [id]
        return Database.execute_sql(sql, params)
    

    @staticmethod
    def add_activiteit(event, date):
        sql = "INSERT INTO Activiteiten (Activiteit, Datum) VALUES (%s, %s)"
        params = [event, date]
        return Database.execute_sql(sql, params)
    

    @staticmethod
    def get_links():
        sql = "SELECT * FROM Links"
        return Database.get_rows(sql)
    

    @staticmethod
    def delete_link(id):
        sql = "DELETE FROM Links WHERE LinkID = %s"
        params = [id]
        return Database.execute_sql(sql, params)
    

    @staticmethod
    def delete_activiteiten(linkID):
        sql = "DELETE FROM Activiteiten WHERE LinkID = %s"
        params = [linkID]
        return Database.execute_sql(sql, params)
    

    @staticmethod
    def add_link(link):
        sql = "INSERT INTO Links (Link) VALUES (%s)"
        params = [link]
        return Database.execute_sql(sql, params)
    

    @staticmethod
    def add_activiteit_not_exists(event, date, linkID):
        sql = "INSERT INTO Activiteiten (Activiteit, Datum, linkID) SELECT * FROM (SELECT %s, %s, %s) AS tmp WHERE NOT EXISTS (SELECT Activiteit, Datum FROM Activiteiten WHERE Activiteit = %s AND Datum = %s AND LinkID = %s)"
        params = [event, date, linkID, event, date, linkID]
        return Database.execute_sql(sql, params)