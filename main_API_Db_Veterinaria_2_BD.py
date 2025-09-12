
# Flask cria o app / request lê o corpo das requisições / response monta as respostas
from flask import Flask, Response, request
# Aqui é como se fosse a ponte para o banco de dados
from flask_sqlalchemy import SQLAlchemy
# Aqui importa os dicionários Python em JSON
import json
# Aqui converte strings de data par objeto 'date'
from datetime import date, datetime

# Aqui é para chamar o servidor web
app = Flask('vet')

# String de conexão ao MySQL com driver e suas credenciais de acesso
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Senai%40134@127.0.0.1/db_clinicavetbd'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# “traduz” entre o mundo dos objetos no Python (classes e atributos) e 
# o mundo das tabelas no banco de dados relacional (linhas e colunas em SQL).
db = SQLAlchemy(app)

# ///////////////////////////////////////////////
# MODELOS
# ///////////////////////////////////////////////
class Vet(db.Model):
    # Nome da tabela no SQL
    __tablename__ = 'tb_clientes'
    # Precisa definir as colunas e tipos (inclusive qual é a primaty key)
    id_cliente = db.Column(db.Integer, primary_key=True)
    nomecliente       = db.Column(db.String(255))
    endereco   = db.Column(db.String(255))
    telefonecliente   = db.Column(db.String(255))

    # relação 1:N (1 cliente pode ter vários pets)
    # permite, pelo objeto Pet, acessar o cliente dono.
    pets = db.relationship('Pet', backref='cliente', lazy=True)

# transforma o objeto Python em um dicionário (para responder a API).
    def to_json(self):
        return {
            'id_cliente': self.id_cliente,
            'nomecliente': self.nomecliente,
            'endereco': self.endereco,
            'telefonecliente': self.telefonecliente,
        }


# Essa class cria um template que espelha a tabela "tb_pets"
class Pet(db.Model):
    __tablename__ = 'tb_pets'
    id_pet          = db.Column(db.Integer, primary_key=True)
    nomepet         = db.Column(db.String(100), nullable=False)
    tipo            = db.Column(db.String(100))
    raca            = db.Column(db.String(100))
    data_nascimento = db.Column(db.Date)
    # cria a chave estrangeira para "tb_clientes"
    # define nomepet e id_cliente como campos obrigatórios
    id_cliente      = db.Column(db.Integer, db.ForeignKey('tb_clientes.id_cliente'), nullable=False)
    idade           = db.Column(db.Integer)

    def to_json(self):
        return {
            'id_pet': self.id_pet,
            'nomepet': self.nomepet,
            'tipo': self.tipo,
            'raca': self.raca,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'id_cliente': self.id_cliente,
            'idade': self.idade
        }

# ///////////////////////////////////////////////
# Funções, bom para padronizar as respostas
# Corpo sempre com os "dados" e "mensagem" opcional
# # ///////////////////////////////////////////////
def gera_resposta(status, conteudo, mensagem=None):
    body = {'dados': conteudo}
    if mensagem:
        body['mensagem'] = mensagem
    return Response(json.dumps(body, ensure_ascii=False), status=status, mimetype='application/json')

def parse_date_or_none(value):
    # Converte string de data "YYYY-MM-DD" para date.
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except Exception:
        return None

# ///////////////////////////////////////////////
# CLIENTES (tb_clientes)
# ///////////////////////////////////////////////
@app.route('/vet', methods=['GET'])
# busca todas as linhas de tb_clientes, converte em lista de JSON e retorna 200.
def lista_clientes():
    clientes = Vet.query.all()
    return gera_resposta(200, [c.to_json() for c in clientes], "Lista de Clientes")

# Faz a busca de cliente por id
@app.route('/vet/<int:id_cliente_par>', methods=['GET'])
def cliente_por_id(id_cliente_par):
    cliente = Vet.query.filter_by(id_cliente=id_cliente_par).first()
    if not cliente:
        return gera_resposta(404, {}, "Cliente não encontrado")
    return gera_resposta(200, cliente.to_json(), "Cliente encontrado")


# Criar um novo registro no banco de dados
@app.route('/vet', methods=['POST'])
def novo_cliente():
    req = request.get_json(silent=True) or {}
    try:
        nomecliente = req.get('nomecliente')
        endereco = req.get('endereco')
        telefonecliente = req.get('telefonecliente')
        if not all([nomecliente, endereco, telefonecliente]):
            return gera_resposta(400, {}, "Campos obrigatórios: nome, endereco, telefone")

        cliente = Vet(nomecliente=nomecliente, endereco=endereco, telefonecliente=telefonecliente)
        # Aqui estou apenas preparando o insert
        db.session.add(cliente)
        # Aqui grava pra valer
        db.session.commit()
        return gera_resposta(201, cliente.to_json(), "Criado com sucesso")
    except Exception as e:
        print('Erro POST /vet:', e)
        # Se der erro, ele desfaz
        db.session.rollback()
        return gera_resposta(400, {}, "Erro ao cadastrar cliente")

# Para alterar um registro
# Ele faz a busca, valida existência e altera campos presentes. Grava com commit()
@app.route('/vet/<int:id_cliente_par>', methods=['PUT'])
def atualiza_cliente(id_cliente_par):
    cliente = Vet.query.filter_by(id_cliente=id_cliente_par).first()
    if not cliente:
        return gera_resposta(404, {}, "Cliente não encontrado")
    req = request.get_json(silent=True) or {}
    try:
        if 'nome' in req: cliente.nome = req['nome']
        if 'endereco' in req: cliente.endereco = req['endereco']
        if 'telefone' in req: cliente.telefone = req['telefone']
        db.session.commit()
        return gera_resposta(200, cliente.to_json(), "Cliente atualizado com sucesso")
    except Exception as e:
        print('Erro PUT /vet:', e)
        db.session.rollback()
        return gera_resposta(400, {}, "Erro ao atualizar cliente")


# Para remover os registros
@app.route('/vet/<int:id_cliente_par>', methods=['DELETE'])
def deleta_cliente(id_cliente_par):
    cliente = Vet.query.filter_by(id_cliente=id_cliente_par).first()
    if not cliente:
        return gera_resposta(404, {}, "Cliente não encontrado")
    try:
        db.session.delete(cliente)
        db.session.commit()
        return gera_resposta(200, cliente.to_json(), "Cliente deletado com sucesso")
    except Exception as e:
        print('Erro DELETE /vet:', e)
        db.session.rollback()
        return gera_resposta(400, {}, "Erro ao deletar cliente")


# ///////////////////////////////////////////////
# PETS (tb_pets)
# ///////////////////////////////////////////////

# GET lista geral de todos os pets
@app.route('/pets', methods=['GET'])
def lista_pets():
    pets = Pet.query.all()
    return gera_resposta(200, [p.to_json() for p in pets], "Lista de Pets")


# GET - Listar por ID do pet
@app.route('/pets/<int:id_pet>', methods=['GET'])
def pet_por_id(id_pet):
    pet = Pet.query.filter_by(id_pet=id_pet).first()
    if not pet:
        return gera_resposta(404, {}, "Pet não encontrado")
    return gera_resposta(200, pet.to_json(), "Pet encontrado")


# GET - Listar pets de um cliente
@app.route('/clientes/<int:id_cliente>/pets', methods=['GET'])
def pets_por_cliente(id_cliente):
    cliente = Vet.query.filter_by(id_cliente=id_cliente).first()
    if not cliente:
        return gera_resposta(404, {}, "Cliente não encontrado")
    return gera_resposta(200, [p.to_json() for p in cliente.pets], "Pets do cliente")


# POST para criar um pet
@app.route('/pets', methods=['POST'])
def novo_pet():
    req = request.get_json(silent=True) or {}
    # Exige que existe o 'nomepet' e 'id_cliente'
    try:
        nomepet = req.get('nomepet')
        id_cliente = req.get('id_cliente')
        if not nomepet or not id_cliente:
            return gera_resposta(400, {}, "Campos obrigatórios: nomepet, id_cliente")

        # confirma se existe um cliente com id_cliente
        if not Vet.query.filter_by(id_cliente=id_cliente).first():
            return gera_resposta(400, {}, "id_cliente inválido (cliente não existe)")

        pet = Pet(
            nomepet=nomepet,
            tipo=req.get('tipo'),
            raca=req.get('raca'),
            # 'parse_date_or_none' protege de vir um valor fora de padrão e converte em data
            data_nascimento=parse_date_or_none(req.get('data_nascimento')),
            id_cliente=id_cliente,
            idade=req.get('idade')
        )
        db.session.add(pet)
        db.session.commit()
        return gera_resposta(201, pet.to_json(), "Pet criado com sucesso")
    except Exception as e:
        print('Erro POST /pets:', e)
        db.session.rollback()
        return gera_resposta(400, {}, "Erro ao cadastrar pet")


# PUT para atualizar um pet
@app.route('/pets/<int:id_pet>', methods=['PUT'])
def atualiza_pet(id_pet):
    pet = Pet.query.filter_by(id_pet=id_pet).first()
    if not pet:
        return gera_resposta(404, {}, "Pet não encontrado")
    req = request.get_json(silent=True) or {}
    try:
        if 'nomepet' in req: pet.nomepet = req['nomepet']
        if 'tipo' in req: pet.tipo = req['tipo']
        if 'raca' in req: pet.raca = req['raca']
        if 'idade' in req: pet.idade = req['idade']
        if 'data_nascimento' in req: pet.data_nascimento = parse_date_or_none(req['data_nascimento'])
        if 'id_cliente' in req:
            novo_cli = Vet.query.filter_by(id_cliente=req['id_cliente']).first()
            if not novo_cli:
                return gera_resposta(400, {}, "id_cliente inválido (cliente não existe)")
            pet.id_cliente = req['id_cliente']

        db.session.commit()
        return gera_resposta(200, pet.to_json(), "Pet atualizado com sucesso")
    except Exception as e:
        print('Erro PUT /pets:', e)
        db.session.rollback()
        return gera_resposta(400, {}, "Erro ao atualizar pet")


# DELETE em um pet por meio do seu id
@app.route('/pets/<int:id_pet>', methods=['DELETE'])
def deleta_pet(id_pet):
    pet = Pet.query.filter_by(id_pet=id_pet).first()
    if not pet:
        return gera_resposta(404, {}, "Pet não encontrado")
    try:
        db.session.delete(pet)
        db.session.commit()
        return gera_resposta(200, pet.to_json(), "Pet deletado com sucesso")
    except Exception as e:
        print('Erro DELETE /pets:', e)
        db.session.rollback()
        return gera_resposta(400, {}, "Erro ao deletar pet")


# ///////////////////////////////////////////////
# Colocar para rodar
# ///////////////////////////////////////////////
if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)
