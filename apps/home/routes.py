# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, jsonify, flash, redirect
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps import db, login_manager
from sqlalchemy import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import column_property
import datetime
import mysql.connector
import pytz
import csv
import io

class Residencia(db.Model):
    __tablename__ = 'Residencia'
    
    ResidenciaId1 = db.Column(db.Integer, primary_key=True, autoincrement=True)
    NombreResidencia = db.Column(db.String(200), nullable=False)
    Direccion = db.Column(db.String(300), nullable=False)
    FechaRegistro = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Tegucigalpa')))
    Estado = db.Column(db.Boolean, nullable=False)
    Ultimaactualizacion  = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Tegucigalpa')))


    def __repr__(self):
        return f'<Residencia {self.NombreResidencia}>'


"""
class Residente(db.Model):
    __tablename__ = 'Residente'
    
    ResidenteId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Codigo = db.Column(db.String(20), nullable=False)
    Nombres = db.Column(db.String(200), nullable=False)
    Apellidos = db.Column(db.String(200), nullable=False)
    FechaRegistro = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Tegucigalpa')), nullable=True)
    Celular = db.Column(db.String(50), nullable=False)
    NumeroCasa = db.Column(db.String(20), nullable=True)
    Calle = db.Column(db.String(20), nullable=True)
    FotoPerfil = db.Column(db.String(200), nullable=True)
    Estado = db.Column(db.Boolean, nullable=False)
    ResidenciaId1 = db.Column(db.Integer, db.ForeignKey('Residencia.ResidenciaId1'), nullable=False)
    ResidenciaId2 = db.Column(db.Integer, nullable=True)
    ResidenciaId3 = db.Column(db.Integer, nullable=True)
    Pagos = db.Column(db.DateTime, nullable=True)

    residencia = db.relationship('Residencia', backref=db.backref('residentes', lazy=True))
"""
class Residente(db.Model):
    __tablename__ = 'Residente'
    
    ResidenteId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Codigo = db.Column(db.String(20), nullable=False)
    Nombres = db.Column(db.String(200), nullable=False)
    Apellidos = db.Column(db.String(200), nullable=False)
    # Define la columna con timezone=True para manejar zonas horarias en SQLAlchemy
    FechaRegistro = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=True)
    Celular = db.Column(db.String(50), nullable=False)
    NumeroCasa = db.Column(db.String(20), nullable=True)
    Calle = db.Column(db.String(20), nullable=True)
    FotoPerfil = db.Column(db.String(200), nullable=True)
    Estado = db.Column(db.Boolean, nullable=False)
    ResidenciaId1 = db.Column(db.Integer, db.ForeignKey('Residencia.ResidenciaId1'), nullable=False)
    ResidenciaId2 = db.Column(db.Integer, nullable=True)
    ResidenciaId3 = db.Column(db.Integer, nullable=True)
    Pagos = db.Column(db.DateTime(timezone=True), nullable=True)

    residencia = db.relationship('Residencia', backref=db.backref('residentes', lazy=True))

    # Utiliza column_property para manejar la conversión de zona horaria
    @column_property
    def FechaRegistro_tz(self):
        if self.FechaRegistro:
            return self.FechaRegistro.astimezone(pytz.timezone('America/Tegucigalpa')).isoformat()

    @column_property
    def Pagos_tz(self):
        if self.Pagos:
            return self.Pagos.astimezone(pytz.timezone('America/Tegucigalpa')).isoformat()


class Accesos(db.Model):
    __tablename__ = 'Accesos'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, nullable=False)
    residenciales = db.Column(db.Integer, nullable=False)


#    def __repr__(self):
#        return f'<Accesos(id={self.id}, residenciales={self.residenciales})>'

#    residencia = db.relationship('Residencia', primaryjoin='Accesos.residenciales == Residencia.ResidenciaId', lazy='select')
#    def __init__(self, residenciales=None):
#        self.residenciales = residenciales

@blueprint.route('/index')
@blueprint.route('/tables')
@blueprint.route('/tables.html')
#@blueprint.route('/residentes')
@login_required
def index():
#    residencia = Residencia.query.all()
    #privilegios= Users.query.filter_by(id=current_user.id).all()
    if current_user.is_authenticated:
        #print(" el privilegio de este usuario es : "+str(current_user.privilegio))
        if current_user.privilegio=='1':
            residencia = Residencia.query.all()
        else:
            accesos = Accesos.query.filter_by(user=current_user.id).all()
            cols=[]
            for item in accesos:
                cols.append(item.residenciales)
            residencia = Residencia.query.filter(Residencia.ResidenciaId1.in_(cols)).all()
    
    return render_template('home/tables.html', residencia=residencia, )


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

@blueprint.route('/tablas/<id>')
@login_required
def residentes(id):
    # Realiza la consulta para obtener los residentes asociados al id de la residencia
    residentes = Residente.query.filter_by(ResidenciaId1=id).order_by(Residente.Nombres).all()

    # Renderiza los resultados en una plantilla
    return render_template('home/residentes.html', residentes=residentes,numeroresidencia=id)

@blueprint.route('/toggle_estado/<int:residente_id>', methods=['POST'])
def toggle_estado(residente_id):
    residente = Residente.query.get_or_404(residente_id)  # Obtener el residente por su ID
    residente.Estado = not residente.Estado  # Cambia el estado a su opuesto (Activo a Inactivo y viceversa)

    try:
        db.session.commit()  # Guardar el cambio en la base de datos
        return jsonify({'estado': residente.Estado})  # Devolver el nuevo estado como JSON
    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({'error': str(e)}), 500  # Devolver mensaje de error en caso de fallo




def obtener_listado_accesos():
    """ DB_SERVER = 'residencial.cn8k44ascgyp.us-east-1.rds.amazonaws.com'
    DB_USER = 'admin'
    DB_PASSWORD = 'j&>_RS;9vKect2P'
    DB_NAME = 'Residencial'
    conn=pymssql.connect(DB_SERVER, DB_USER, DB_PASSWORD, DB_NAME)
    cursor=conn.cursor()
    user_id = current_user.id
    query="SELECT * FROM Accesos WHERE id=%s"
    cursor.execute(query, (user_id,))
    accesos = cursor.fetchall()
    cursor.close()
    conn.close()
    # Consulta para agrupar `ResidenciaId` por `id` de la tabla `Accesos` 
    residenciales_ids = [acceso[1] for acceso in accesos]
    residencias = Residencia.query.filter(Residencia.ResidenciaId.in_(residenciales_ids)).all()
    resultados = db.session.query(Residencia).join(Residente).join(Accesos, Residente.ResidenciaId == Accesos.residenciales).all()"""
    residencias = db.session.query(Residencia).all()
    print(residencias)

    return residencias


@blueprint.route('/delete_residente', methods=['POST'])
def delete_residente():
    data = request.get_json()
    residente_id = data.get('residente_id')
    token = data.get('token')

    # Validar el token (esta es una validación ficticia, deberías implementar la lógica real)
    if token != '9tQDMN0&U3':
        return jsonify({'message': 'No Autorizado'}), 403

    residente = Residente.query.get(residente_id)
    if residente is None:
        return jsonify({'message': 'Residente no encontrado'}), 404

    db.session.delete(residente)
    db.session.commit()
    return jsonify({'message': 'Residente eliminado correctamente'}), 200


@blueprint.route('/add_residente', methods=['POST'])
def add_residente():
    data = request.json
    token = data.get('token')
    
    # Aquí debes verificar el token para la seguridad
    if token != '9tQDMN0&U3':  # Reemplaza con la lógica real de verificación del token
        return jsonify({'message': datetime.datetime.now()}), 401

    nuevo_residente = Residente(
        Codigo=data['codigo'],
        Nombres=data['nombres'],
        Apellidos=data['apellidos'],
        FechaRegistro=datetime.datetime.now(),
        Celular=data['celular'],
        NumeroCasa=data.get('numeroCasa'),
        Calle=data.get('calle'),
        FotoPerfil=data.get('fotoPerfil'),
        Estado=data['estado'] == 'true',
        ResidenciaId1=data['residenciaId']  # Asigna el ID de la residencia correspondiente
    )
    db.session.add(nuevo_residente)
    db.session.commit()

    return jsonify({'message': 'Residente agregado correctamente', 'residente': {
        'ResidenteId': nuevo_residente.ResidenteId,
        'Codigo': nuevo_residente.Codigo,
        'Nombres': nuevo_residente.Nombres,
        'Apellidos': nuevo_residente.Apellidos,
        'Celular': nuevo_residente.Celular,
        'NumeroCasa': nuevo_residente.NumeroCasa,
        'Calle': nuevo_residente.Calle,
        'FotoPerfil': nuevo_residente.FotoPerfil,
        'Estado': nuevo_residente.Estado
    }})

@blueprint.route('/residentes', methods=['GET', 'POST'])
def holamundo():
    return "HOla Mundo"

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

@blueprint.route('/get_residentes', methods=['POST'])
def get_residentes():
    data = request.get_json()
    residencia_id = data.get('ResidenciaId1')
    token=data.get('token')
    print(residencia_id)
    if token!="9tQDMN0&U3":
        return jsonify({'error': 'No Autorizado'}), 400

    if not residencia_id:
        return jsonify({'error': 'Debe proporcionar ResidenciaId'}), 400
    try:
        # Consulta a la base de datos para obtener los residentes
        residentes = Residente.query.filter_by(ResidenciaId1=residencia_id).all()

        # Preparar la respuesta
        residentes_list = []
        for residente in residentes:
            residente_data = {
                'ResidenteId': residente.ResidenteId,
                'Codigo': residente.Codigo,
                'Nombres': residente.Nombres,
                'Apellidos': residente.Apellidos,
                'FechaRegistro': residente.FechaRegistro if residente.FechaRegistro else None,
                'Celular': residente.Celular,
                'NumeroCasa': residente.NumeroCasa,
                'Calle': residente.Calle,
                'FotoPerfil': residente.FotoPerfil,
                'Estado': residente.Estado,
                'ResidenciaId1': residente.ResidenciaId1,
                'Pagos': residente.Pagos if residente.Pagos else None
            }
            residentes_list.append(residente_data)

        return jsonify({'residentes': residentes_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blueprint.route('/edit_residente/<int:residente_id>', methods=['PUT'])
def edit_residente(residente_id):
    data = request.json
    token = data.get('token')

    # Verificar el token para la seguridad
    if token != '9tQDMN0&U3':  # Reemplaza con la lógica real de verificación del token
        return jsonify({'message': 'Token inválido'}), 401

    residente = Residente.query.get_or_404(residente_id)
    residente.Codigo = data['codigo']
    residente.Nombres = data['nombres']
    residente.Apellidos = data['apellidos']
    residente.Celular = data['celular']
    residente.NumeroCasa = data.get('numeroCasa')
    residente.Calle = data.get('calle')
    residente.FotoPerfil = data.get('fotoPerfil')
    residente.Estado = data['estado'] == 'true'

    db.session.commit()

    return jsonify({'message': 'Residente editado correctamente', 'residente': {
        'ResidenteId': residente.ResidenteId,
        'Codigo': residente.Codigo,
        'Nombres': residente.Nombres,
        'Apellidos': residente.Apellidos,
        'Celular': residente.Celular,
        'NumeroCasa': residente.NumeroCasa,
        'Calle': residente.Calle,
        'FotoPerfil': residente.FotoPerfil,
        'Estado': residente.Estado
    }})

@blueprint.route('/cargar_csv/<int:numeroresidencia>', methods=['POST'])
@login_required
def cargar_csv(numeroresidencia):
    if request.method == 'POST':
        # Verificar que se haya enviado un archivo CSV
        if 'archivo_csv' not in request.files:
            flash('No se encontró el archivo CSV')
            return redirect(request.url)

        archivo = request.files['archivo_csv']

        # Verificar que se haya seleccionado un archivo
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo')
            return redirect(request.url)

        # Leer el archivo CSV y procesar los datos
        if archivo:
            # Leer los datos del archivo CSV
            stream = io.StringIO(archivo.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.reader(stream)

            # Saltar la primera fila si contiene encabezados
            next(csv_reader, None)  # skip the headers
            print("se recibio archivo csv se entra al loop")
            for row in csv_reader:
                # Guardar los datos en la base de datos
                print(str(row[0])+" residencia : "+str(id))
                if row[0]=="":
                    db.session.rollback()
                    return flash('No pueden haber codigos vacios')
                nuevo_residente = Residente(
                                    Codigo=str(row[0]) if row[0] else None,
                                    Nombres=str(row[1]) if row[1] else None,
                                    Apellidos=str(row[2]) if row[2] else None,
                                    FechaRegistro=datetime.datetime.now(),
                                    Celular=str(row[3]) if row[3] else None,
                                    NumeroCasa=str(row[4]) if row[4] else None,
                                    Calle=str(row[5]) if row[5] else None,
                                    FotoPerfil=None,
                                    Estado=True,
                                    ResidenciaId1=numeroresidencia  # Asigna el ID de la residencia correspondiente
                                )
                db.session.add(nuevo_residente)
            db.session.commit()
            flash('Datos cargados exitosamente desde el archivo CSV.')
    return redirect('/tablas/'+str(numeroresidencia))
