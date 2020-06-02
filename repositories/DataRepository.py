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