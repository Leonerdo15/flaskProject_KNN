import os
import psycopg2
from flask import Flask
from dotenv import load_dotenv
from flask import jsonify, abort
from knn import sugere_para
from flask import make_response

load_dotenv()

app = Flask(__name__)
url = os.getenv('DATABASE_URL')
conection = psycopg2.connect(url)


def generate_csv(data, header):
    header = header.replace("\n", "")
    arr_header = header.split(",")
    output = []
    output.append(header + "\n")
    for item in data:
        string = str(item[arr_header[0]]) + "," + str(item[arr_header[1]]) + "," + str(item[arr_header[2]])
        output.append(string)
    output_string = "\n".join(output)
    return output_string


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def get_spot_data():
    cursor = conection.cursor()
    cursor.execute("SELECT sp_id, sp_name, st_name FROM spots inner join spot_types st on st.st_id = spots.sp_st_id")
    spots = cursor.fetchall()
    return [{"movieId": sp[0], "title": sp[1], "genders":sp[2]} for sp in spots]


@app.route('/spots.csv', methods=['GET'])
def get_spots():
    csv_data = generate_csv(get_spot_data(), "movieId,title,genders\n")
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=spots.csv"
    response.headers["Content-type"] = "text/csv"
    return response


def get_evaluation_data():
    cursor = conection.cursor()
    cursor.execute("select se_us_id, se_sp_id, se_rate from spot_evaluations")
    spots_evaluations = cursor.fetchall()
    return [{"usuarioId": se[0], "filmeId": se[1], "nota": se[2]} for se in spots_evaluations]


@app.route('/spotsEvaluations.csv', methods=['GET'])
def get_spots_evaluations():
    csv_data = generate_csv(get_evaluation_data(), "usuarioId,filmeId,nota\n")
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=spots_evaluations.csv"
    response.headers["Content-type"] = "text/csv"
    return response


@app.route('/recomendations/<int:user_id>', methods=['GET'])
def get_recomendation(user_id):
    recomendations = sugere_para(user_id)
    recomendations = recomendations.to_json(orient='records')
    return recomendations


if __name__ == '__main__':
    app.run()
