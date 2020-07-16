import requests
import sqlite3
import time
from flask import Flask
from flask_restplus import Api, Resource, reqparse

# create a flask_restplus application
app = Flask(__name__)
api = Api(app)

# query parameters
parser_indicator_id = reqparse.RequestParser()
parser_indicator_id.add_argument("indicator_id", required=True,
                                 help="An indicator in http://api.worldbank.org/v2/indicators")
parser_order_by = reqparse.RequestParser()
parser_order_by.add_argument("order_by", required=True, help="sort collections by your input columns {+id,"
                                                             "+creation_time,+indicator,-id,-creation_time,-indicator}")

parser_top_bottom = reqparse.RequestParser()
parser_top_bottom.add_argument("q", required=True)


@api.route("/collections")
class Indicator(Resource):

    @api.expect(parser_indicator_id)
    def post(self):

        args = parser_indicator_id.parse_args()

        # retrieve the query parameter
        # 1.0.HCount.Vul4to10
        # DT.AMT.DLTT.CD.OT.AR.1824.US
        # DT.AMT.DECT.CD.03.US
        indicator_id = args.get("indicator_id")

        url = "http://api.worldbank.org/v2/countries/all/indicators/" + indicator_id + \
              "?date=2012:2017&format=json&per_page=1000"

        # print("test1")
        content = requests.get(url)
        # print("test2")
        data = content.json()
        # print("test3")

        if len(data) != 2:
            return {"message": "Indicator {} does not exist".format(indicator_id)}, 404

        all_data_cursor = c.execute("SELECT INDICATOR_ID FROM INDICATOR")
        exist_indicator_id = all_data_cursor.fetchall()
        # print(exist_indicator_id)
        for t in exist_indicator_id:
            if indicator_id in t:
                return {"message": "Indicator {} already exist".format(indicator_id)}, 409

        # use the record id in the record id table, and add 1 to the current record
        current_id = 0
        recorder_c = c.execute("SELECT RECORDER FROM ID_RECORDER")
        for i in recorder_c:
            current_id = i[0] + 1
        c.execute("UPDATE ID_RECORDER SET RECORDER = {}".format(current_id))

        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        current_uri = "/collection/" + str(current_id)

        # update indicator_value in the db
        # the indicator value is in the second element in the list, sometimes this value is null
        try:
            indicator_value = data[1][0]["indicator"]["value"]
        except TypeError:
            indicator_value = ""
        c.execute(
            "INSERT INTO INDICATOR (URI, ID, CREATION_TIME, INDICATOR_ID, INDICATOR_VALUE) VALUES (?, ?, ?, ?, ?)",
            (current_uri, current_id, current_time, indicator_id, indicator_value))
        conn.commit()

        # handle the situation when data[1] is null
        try:
            for dic in data[1]:
                country = dic["country"]["value"]
                year = dic["date"]
                value = dic["value"]
                c.execute("INSERT INTO ENTITY (ID, COUNTRY, YEAR, VALUE) VALUES(?, ?, ?, ?)",
                          (current_id, country, year, value))
        except TypeError:
            pass

        conn.commit()

        return {"uri": current_uri,
                "id": current_id,
                "creation_time": current_time,
                "indicator_id": indicator_id
                }

    @api.expect(parser_order_by)
    def get(self):
        args = parser_order_by.parse_args()

        # retrieve the query parameters
        order_by = args.get("order_by")

        # remove the space in the input order and get the list of order columns
        order_by = order_by.replace(" ", "")
        order_list = order_by.split(",")

        for order in order_list:
            if order not in ["+id", "+creation_time", "+indicator", "-id", "-creation_time", "-indicator"]:
                return {"message": "invalid order_by"}, 400

        # get data from db
        result = []
        all_data_cursor = c.execute("SELECT * FROM INDICATOR")
        for i in all_data_cursor:
            indicator_dic = {"uri": i[0],
                             "id": i[1],
                             "creation_time": i[2],
                             "indicator": i[3]
                             }
            result.append(indicator_dic)
        # print(order_list)

        """
        for elements who have the same high priority key, the order of these elements do not change by using sort
         function, so they keep the order which is decided by the lower priority
        # the first order in the order have the highest priority
        # reverse the order list to begin with the lowest priority 
        # sort the list from the lowest priority to the highest priority
        """

        order_list.reverse()
        for order in order_list:
            result.sort(key=lambda item: item[order[1:]], reverse=(order[0: 1] == "-"))

        return result


@api.route("/collections/<int:id>")
class Collection(Resource):
    def delete(self, id):
        # delete information in the indicator table
        id_cursor = c.execute("SELECT * FROM INDICATOR WHERE ID == {}".format(id))
        if len(list(id_cursor)) == 0:
            return {"message": "The collection {} does not found".format(id)}, 404

        c.execute("DELETE FROM INDICATOR WHERE ID == {}".format(id))
        conn.commit()

        # delete information in the entity table
        c.execute("DELETE FROM ENTITY WHERE ID == {}".format(id))
        conn.commit()

        return {"message": "The collection {} was removed from the database.".format(id)}, 200

    def get(self, id):
        entities = []
        all_entities_cursor = c.execute("SELECT * FROM ENTITY WHERE ID == {}".format(id))
        for i in all_entities_cursor:
            entity_dic = {"country": i[1],
                          "date": i[2],
                          "value": i[3]
                          }
            entities.append(entity_dic)
        # print(entities)
        indicator_cursor = c.execute("SELECT * FROM INDICATOR WHERE ID == {}".format(id))
        if len(list(indicator_cursor)) == 0:
            return {"message": "The collection {} does not found".format(id)}, 404

        indicator_cursor = c.execute("SELECT * FROM INDICATOR WHERE ID == {}".format(id))
        result_dic = {}
        for i in indicator_cursor:
            result_dic = {"id": i[1],
                          "indicator": i[3],
                          "indicator_value": i[4],
                          "creation_time": i[2],
                          "entries": entities
                          }
        return result_dic


@api.route("/collections/<int:id>/<int:year>/<string:country>")
class Value(Resource):
    def get(self, id, year, country):
        economic_entity_cursor = c.execute("SELECT * FROM ENTITY WHERE ID == ? AND YEAR == ? AND COUNTRY == ?",
                                           (id, year, country))

        if len(list(economic_entity_cursor)) == 0:
            return {"message": "The collection {} year {} country {} does not found".format(id, year, country)}, 404

        economic_entity_cursor = c.execute("SELECT * FROM ENTITY WHERE ID == ? AND YEAR == ? AND COUNTRY == ?",
                                           (id, year, country))
        value = -1
        for i in economic_entity_cursor:
            value = i[3]

        economic_indicator_cursor = c.execute("SELECT INDICATOR_ID FROM INDICATOR WHERE ID == {}".format(id))
        indicator = ""
        for i in economic_indicator_cursor:
            indicator = i[0]

        return {"id": id,
                "indicator": indicator,
                "country": country,
                "year": year,
                "value": value
                }


@api.route("/collections/<int:id>/<int:year>")
class TopBottom(Resource):

    @api.expect(parser_top_bottom)
    def get(self, id, year):
        args = parser_top_bottom.parse_args()

        # retrieve q
        q = args.get("q")

        if q[0] not in ["+", "-"]:
            return {"message": "invalid q"}, 400

        entries = []
        all_entities_cursor = c.execute("SELECT COUNTRY, VALUE FROM ENTITY WHERE ID = ? AND YEAR = ?", (id, year))

        if len(list(all_entities_cursor)) == 0:
            return {"message": "The collection {} year {} does not found".format(id, year)}, 404

        all_entities_cursor = c.execute("SELECT COUNTRY, VALUE FROM ENTITY WHERE ID = ? AND YEAR = ?", (id, year))
        for i in all_entities_cursor:
            entity_dic = {"country": i[0],
                          "value": i[1]
                          }
            if entity_dic["value"] is not None:
                entries.append(entity_dic)

        # get top/bottom entries
        entries.sort(key=lambda item: item["value"], reverse=(q[0] == "+"))
        q = int(q[1:])
        if len(entries) <= q:
            pass
        else:
            entries = entries[0: q]

        result = {}
        indicator_cursor = c.execute("SELECT INDICATOR_ID, INDICATOR_VALUE FROM INDICATOR WHERE ID == {}".format(id))
        for i in indicator_cursor:
            result = {"indicator": i[0],
                      "indicator_value": i[1],
                      "entries": entries
                      }
        return result


if __name__ == "__main__":
    # connect to database
    conn = sqlite3.connect("world_bank.db", check_same_thread=False)
    c = conn.cursor()
    # if indicator table not exist create the table
    try:
        c.execute(
            "CREATE TABLE INDICATOR (URI TEXT, ID INT, CREATION_TIME TEXT, INDICATOR_ID TEXT, INDICATOR_VALUE, TEXT)")
        c.execute("CREATE TABLE ENTITY (ID INT, COUNTRY TEXT, YEAR INT, VALUE INT)")

        # this is a table used to count number and used this unique number as id of the indicator
        c.execute("CREATE TABLE ID_RECORDER (RECORDER INT)")
        c.execute("INSERT INTO ID_RECORDER (RECORDER) VALUES(0)")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    app.run(debug=True)
