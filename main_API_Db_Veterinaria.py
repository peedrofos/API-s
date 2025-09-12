# Atividade Banco Relacional veterinária

from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask('vet')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Senai%40134@127.0.0.1/db_vet'

dbvet = SQLAlchemy(app)

class Vet (dbvet.Model):
    _tablename_ = 'tb_clientes'
    id_cliente = dbvet.Column(dbvet.Integer, primary_key=True)
    nome = dbvet.Column(dbvet.String(255))
    endereco = dbvet.Column(dbvet.String(255))
    telefone = dbvet.Column(dbvet.String(255))
    def to_json(self):
        return {
            'id_cliente': self.id_cliente,
            'nome': self.nome,
            'endereco': self.endereco,
            'telefone': self.telefone,
        }
    
def gera_resposta(status, conteudo, mensagem=False):
    body = {}
    body['dados'] = conteudo 
    if (mensagem):
        body['mensagem'] = mensagem
    return Response(json.dumps(body), status=status, mimetype='application/json')

# GET 
@app.route('/vet', methods=['GET'])
def seleciona_cliente():
    cliente_selecionado = Vet.query.all()
    cliente_json = [cliente.to_json() for cliente in cliente_selecionado]
    return gera_resposta(200, cliente_json, "Lista de Clientes")

# GET POR ID
@app.route('/vet/<id_cliente_par>', methods=['GET'])
def seleciona_cliente_por_id(id_cliente_par):
    cliente_selecionado = Vet.query.filter_by(id_cliente=id_cliente_par).first()
    
    if not cliente_selecionado:
        return gera_resposta(404, {}, "Cliente não encontrado")

    cliente_json = cliente_selecionado.to_json()
    return gera_resposta(200, cliente_json, 'Cliente encontrado')

# POST 
@app.route('/vet', methods=['POST'])
def novo_cliente():
    requisicao = request.get_json()
    try:
        cliente = Vet(
            nome = requisicao['nome'],
            endereço = requisicao['endereco'],
            telefone = requisicao['telefone']
        )
        dbvet.session.add(cliente)
        dbvet.session.commit()
        return gera_resposta(201, cliente.to_json(), 'Criado com Sucesso')
    except Exception as e:
        print('Erro', e)
        return gera_resposta(400, {}, "Erro ao Cadastrar!")
    
# DELETE
@app.route('/vet/<id_cliente_par>', methods=['DELETE'])
def deleta_vet(id_cliente_par):
    vet = Vet.query.filter_by(id_cliente=id_cliente_par).first()

    if not vet:
        return gera_resposta(404, {}, "vet não encontrado")

    try:
        dbvet.session.delete(vet)
        dbvet.session.commit()
        return gera_resposta(200, vet.to_json(), 'Deletado com Sucesso')
    except Exception as e:
        print('Erro', e)
        return gera_resposta(400, {}, "Erro ao Deletar")

#  UPDATE
@app.route("/vet/<id_cliente_par>", methods=['PUT'])
def atualiza_vet(id_cliente_par):
    cliente = Vet.query.filter_by(id_cliente=id_cliente_par).first()
    requisicao = request.get_json()

    try:
        if ('nome' in requisicao):
            cliente.nome = requisicao['nome']

        if ('endereco' in requisicao):
            cliente.endereco = requisicao['endereco']

        if ('telefone' in requisicao):
            cliente.telefone = requisicao['telefone']

        dbvet.session.add(cliente)
        dbvet.session.commit()
        return gera_resposta(200, cliente.to_json(), 'Cliente Atualizado com Sucesso')
    except Exception as e:
        print('Erro', e)
        return gera_resposta(400, {}, "Erro ao Atualizar")

if _name_ == '_main_':
    app.run(port=5000, host='localhost', debug=True)