# pip install flask
from flask import Flask, request, make_response, jsonify

# Importação da base de dados
from bd import carros

# Esse módulo do Flask vai subir a nossa API localmente
# Vamos instanciar o módulo Flask na nossa variável app
app = Flask('carros')


# MÉTODO 1 - Visualização de Dados 
# COMANDO: GET

# 1º O que esse método vai fazer?
# 2º Onde ele vai fazer?
# Sempre pensar nesta estrutura.

@app.route('/carrinho', methods=['GET'])
def get_carros():
    return carros


# MÉTODO 1.1 - VISUALIZAÇÃO DE DADOS POR ID (GET)
@app.route('/carrinho/<int:id_parametro>', methods=['GET'])
def get_carros_id(id_parametro):
    for carro in carros:
        if carro.get('id') == id_parametro:
            return jsonify(carro)


# METODO 2 - CRIAÇÃO DE NOVOS REGISTROS (POST)
# Verificar os daos que estão sendo passados na requisição e armazena na nossa base

@app.route('/carrinho', methods=['POST'])
def criar_carro():
    carro = request.get_json()
    carros.append(carro)
    return make_response(
        jsonify(
            mensagem = 'Carro cadastrado com sucesso!',
            carrinho = carro
        )
    )


# MÉTODO 3 - DELETAR REGISTROS (DELETE)
@app.route('/carrinho/<int:id>', methods=['DELETE'])
def excluir_carro(id):
    for indice, carro in enumerate(carros):
        if carro.get('id') == id:
            del carros[indice]
            return jsonify(
                {'mensagem': "Carro Excluído"}
            )



# MÉTODO 4 - EDITAR OS REGISTROS (PUT)
@app.route('/carrinho/<int:id>', methods=['PUT'])
def alterar_carro(id):
    carro_alterado = request.get_json()
    for indice, carro in enumerate(carros):
        if carro.get('id') == id:
            carros[indice].update(carro_alterado)
            return jsonify(
                carros[indice]
                )






app.run(port=5000, host='localhost', debug=True)