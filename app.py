from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import random

# Configuración inicial
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:111019As@localhost:3306/medical_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Modelo de la base de datos
class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    diagnosis = db.Column(db.String(255), nullable=True)
    contact_info = db.Column(db.String(255), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)

# Esquema con Marshmallow
class PatientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Patient
        load_instance = True

# Datos de ejemplo
def generate_sample_data():
    first_names = ['John', 'Jane', 'Alice', 'Bob', 'Eve', 'Charlie', 'Diana', 'Mike', 'Anna', 'Tom']
    last_names = ['Smith', 'Doe', 'Brown', 'Taylor', 'Johnson', 'White', 'Martin', 'Lee', 'Walker', 'Hall']
    diagnoses = ['Hypertension', 'Diabetes', 'Asthma', 'Flu', 'Migraine', 'Allergy', 'Fracture', 'Infection', 'Anxiety', 'Obesity']

    for _ in range(100):
        patient = Patient(
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            age=random.randint(1, 100),
            gender=random.choice(['Male', 'Female']),
            diagnosis=random.choice(diagnoses),
            contact_info=f'+1-{random.randint(100,999)}-{random.randint(1000,9999)}',
            appointment_date=f'2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}'
        )
        db.session.add(patient)
    db.session.commit()

if __name__ == '__main__':
    # Envolver en un contexto de aplicación
    with app.app_context():
        # Crear la base de datos si no existe
        db.create_all()
        print("Base de datos creada correctamente.")

        # Generar datos de muestra
        generate_sample_data()
        print("Datos de ejemplo añadidos.")
