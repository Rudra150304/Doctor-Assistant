#doctor-assistant/backend/app/models.py
from sqlalchemy import Column, Integer, String, Date, Time
from .db import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer)
    patient_name = Column(String)

    date = Column(Date)
    time = Column(Time)

    status = Column(String, default="booked")
