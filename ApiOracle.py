from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import cx_Oracle
import os

app = Flask(__name__)

# Configuração do Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = '160919'  # chave de criptografia
jwt = JWTManager(app)


# diretorio path
os.environ['PATH'] = r'C:\instantclient_21_9;' + os.environ['PATH']

# Detalhes de conexão
dsn_tns = cx_Oracle.makedsn('ip', 1521, service_name='WINT')

# Configuração do pool de conexões
pool = cx_Oracle.SessionPool(user='login', password='senha', dsn=dsn_tns, min=1, max=5, increment=1, encoding='UTF-8')

# Função auxiliar para executar consultas
def executar_consulta(query):
    connection = pool.acquire()
    cursor = connection.cursor()

    try:
        cursor.execute(query)
        resultado = cursor.fetchall()

        # Converte o resultado para um formato JSON
        dados_json = []
        for linha in resultado:
            dados_json.append({
                'CODPROD': linha[0],
                'CODAUXILIAR': linha[1],
                'VALORULTENT': linha[2]
            })

        return dados_json

    except Exception as e:
        raise e

    finally:
        # Libera o banco de dados
        cursor.close()
        pool.release(connection)

# Rota para obter dados
@app.route('/consulta', methods=['GET'])
@jwt_required()
def obter_dados():
    try:
        query = 'SELECT CODPROD,CODAUXILIAR,VALORULTENT FROM API_ECOMMERCE'
        resultado = executar_consulta(query)

        return jsonify({'dados': resultado})

    except Exception as e:
        return jsonify({'erro': str(e)})

# Rota para autenticação e obtenção de token
@app.route('/login', methods=['POST'])
def login():
    # autenticação
    if request.json.get('username') == '****' and request.json.get('password') == '****':
        access_token = create_access_token(identity=request.json.get('username'))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Credenciais inválidas"}), 401

if __name__ == '__main__':
    # ip/porta
    ip = '0.0.0.0'  # Isso fará com que o Flask escute em todos os IPs disponíveis
    porta = 5000

    # Execute o aplicativo Flask
    app.run(host=ip, port=porta)
