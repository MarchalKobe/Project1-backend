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
        sql = 'SELECT Datum, Waarde FROM Historiek WHERE ApparaatID = %s AND Datum LIKE %s ORDER BY Datum'
        params = [sensorid, date]
        return Database.get_rows(sql, params)