# SQL_ALCHEMY
# pip install flask_sqlalchemy
# Permite a conexão da API com o banco de dados
# Flask - Permite a criação de API com Python
# Response e request - Requisição 

from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask('carros')

# Abaixo vai rastrear as modificações realizadas
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True

# Configuração de conexão com o banco
# 1ª informação é usuário (root) 
# 2ª senha (Senai@134)
# %40 é o que substituio @
# 3ª localhost (127.0.0.1)
# 4ª nome do seu banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Senai%40134@127.0.0.1/db_carro'

mybd = SQLAlchemy(app) 

# Classe para definir o modelo dos dados que correspondem a tabela do banco de dados
class carros(mybd.Model):
    __tablename__ = 'tb_carro'
    id_carro = mybd.Column(mybd.Integer, primary_key=True)
    marca = mybd.Column(mybd.String(255))
    modelo = mybd.Column(mybd.String(255))
    ano = mybd.Column(mybd.String(255))
    valor = mybd.Column(mybd.String(255))
    cor = mybd.Column(mybd.String(255))
    numero_vendas = mybd.Column(mybd.String(255))

# Esse método to_json vai ser usado para converter o objeto (registro) em json
    def to_json(self):
        return {
            "id_carro": self.id_carro,
            "marca": self.marca,
            "modelo": self.modelo,
            "ano": self.ano,
            "valor": float(self.valor),
            "cor": self.cor,
            "numero_vendas": self.numero_vendas
        }
    
# /////////////////////////////////////////////////////////////////////////////

# 1º MÉTODO - GET
@app.route('/carros', methods = ['GET'])
def seleciona_carro():
    carro_selecionado = carros.query.all()
    # Executa uma consulta no banco de dados - "all" pede para trazer tudo
    # Como se fosse um (SELECT * FROM tb_carro)
    carro_json = [carro.to_json()
                  for carro in carro_selecionado]
    return gera_resposta(200, "Lista de Carros", carro_json)



# /////////////////////////////////////////////////////////////////////////////
# 2º MÉTODO - GET (POR ID)
@app.route('/carros/<id_carro_par>', methods=['GET'])
def seleciona_carro_id(id_carro_par):
    carro_selecionado = carros.query.filter_by(id_carro=id_carro_par).first()
    # seria como se fosse um SELECT * FROM tb_carro WHERE id_carro = "5"
    carro_json = carro_selecionado.to_json()
    return gera_resposta (200, 'Carro', carro_json, 'Carro localizado!')



# /////////////////////////////////////////////////////////////////////////////
# 3º MÉTODO - POST 
@app.route('/carros', methods=['POST'])
def criar_carro():
    requisicao = request.get_json()

    try:
        carro = carros(
            id_carro = requisicao['id_carro'],
            marca = requisicao['marca'],
            modelo = requisicao['modelo'],
            ano = requisicao['ano'],
            valor = requisicao['valor'],
            cor = requisicao['cor'],
            numero_vendas = requisicao['numero_vendas']
        )

        mybd.session.add(carro)
        # Comando para adicionar ao banco
        mybd.session.commit()
        # Comando para salvar a linha de código anterior

        return gera_resposta (201, carro.to_json(), 'Criado com Sucesso!')
    except Exception as e:
        print('Erro', e)

        return gera_resposta(400,{}, 'Erro ao Cadastrar!')


# /////////////////////////////////////////////////////////////////////////////
# 4º MÉTODO - DELETE
@app.route('/carros/<id_carro_par>', methods=['DELETE'])
def deletar_carro(id_carro_par):
    carro_selecionado = carros.query.filter_by(id_carro=id_carro_par).first()
    try:
        mybd.session.delete(carro_selecionado)
        mybd.session.commit()
        return gera_resposta (200, carro_selecionado.to_json(), "Deletado com Sucesso!")
    
    except Exception as e:
        print("Erro", e)
        return gera_resposta (400, {}, "Erro ao Deletar!")



# /////////////////////////////////////////////////////////////////////////////
# 5º MÉTODO - ATUALIZAÇÃO (PUT)
@app.route('/carros/<id_carro_par>', methods=['PUT'])
def atualizar_carro(id_carro_par):
    carro_selecionado = carros.query.filter_by(id_carro=id_carro_par).first()
    requisicao = request.get_json()

    try:
        if ('marca' in requisicao):
            carro_selecionado.marca = requisicao['marca']
        if ('modelo' in requisicao):
            carro_selecionado.modelo = requisicao['modelo']
        if ('ano' in requisicao):
            carro_selecionado.ano = requisicao['ano']
        if ('valor' in requisicao):
            carro_selecionado.valor = requisicao['valor']
        if ('cor' in requisicao):
            carro_selecionado.cor = requisicao['cor']
        if ('numero_vendas' in requisicao):
            carro_selecionado.numero_vendas = requisicao['numero_vendas']

        mybd.session.add(carro_selecionado)
        mybd.session.commit()

        return gera_resposta (200, carro_selecionado.to_json(), "Carro Atualizado com Sucesso")

    except Exception as e:
        print("Erro", e)
        return gera_resposta (400, {}, "Erro ao Atualizar!")











# /////////////////////////////////////////////////////////////////////////////
# Resposta Padrão

def gera_resposta(status, conteudo, mensagem=False):
    # - status (200, 201)
    # - nome do conteúdo
    # - conteúdo
    # - mensagem (opcional)
    body = {}
    body['Lista'] = conteudo
    
    if (mensagem):
        body['mensagem'] = mensagem

    return Response(json.dumps(body), status=status, mimetype='application/json')   
# Dumps converte nosso dicionário criado (body) em Json (json.dumps)




app.run(port=5000, host='localhost', debug=True)


