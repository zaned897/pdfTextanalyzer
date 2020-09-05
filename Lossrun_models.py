from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
import datetime

engine = create_engine('postgresql://postgresql_user:postgresql_password@localhost/db_name', echo=True)
Session = sessionmaker(bind=engine)()
Base = declarative_base()

class TimeDim(Base):
    __tablename__ = 'time_dim'

    timeid = Column(Integer, primary_key = True)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)

    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

class StatusDim(Base):
    __tablename__ = 'status_dim'

    status_id = Column(Integer, primary_key = True)
    status_name = Column(String)
    lossrun_facts = relationship("LossRunFact")

    def __init__(self, status_name):
        self.status_name = status_name

class InsurerDim(Base):
    __tablename__ = 'insurer_dim'

    insurer_id = Column(Integer, primary_key = True)
    insurer_name = Column(String)
    insurer_address = Column(String)
    insurer_status = Column(String)
    lossrun_facts = relationship("LossRunFact")

    def __init__(self, insurer_name, insurer_address, insurer_status):
        self.insurer_name = insurer_name
        self.insurer_address = insurer_address
        self.insurer_status = insurer_status

class InsuredDim(Base):
    __tablename__ = 'insured_dim'

    insured_id = Column(Integer, primary_key = True)
    insured_name = Column(String)
    insured_address = Column(String)
    insured_status = Column(String)
    lossrun_facts = relationship("LossRunFact")

    def __init__(self, insured_name, insured_address, insured_status):
        self.insured_name = insured_name
        self.insured_address = insured_address
        self.insured_status = insured_status

class PolicyDim(Base):
    __tablename__ = 'policy_dim'

    policy_id = Column(Integer, primary_key = True)
    insured_id = Column(Integer)
    insurer_id = Column(Integer)
    policy_number = Column(Integer)
    policy_start_date = Column(DateTime)
    policy_end_date = Column(DateTime)
    policy_status = Column(String)
    lossrun_facts = relationship("LossRunFact")

    def __init__(self, insured_id, insurer_id, policy_number, policy_start_date, policy_end_date, policy_status):
        self.insured_id = insured_id
        self.insurer_id = insurer_id
        self.policy_number = policy_number
        self.policy_start_date = policy_start_date
        self.policy_end_date = policy_end_date
        self.policy_status = policy_status

class LossRunReportDim(Base):
    __tablename__ = 'lossrunreport_dim'

    lossrunreport_id = Column(Integer, primary_key = True)
    lossrunreport_load_date = Column(DateTime)
    lossrunreport_date = Column(DateTime)
    lossrun_facts = relationship("LossRunFact")

    def __init__(self, lossrunreport_load_date, lossrunreport_date):
        self.lossrunreport_load_date = lossrunreport_load_date
        self.lossrunreport_date = lossrunreport_date

class ReportGeneratorDim(Base):
    __tablename__ = 'reportgenerator_dim'

    reportgenerator_id = Column(Integer, primary_key = True)
    reportgenerator_name = Column(String)
    reportgenerator_address = Column(String)
    reportgenerator_status = Column(String)
    lossrun_facts = relationship("LossRunFact")

    def __init__(self, reportgenerator_name, reportgenerator_address, reportgenerator_status):
        self.reportgenerator_name = reportgenerator_name
        self.reportgenerator_address = reportgenerator_address
        self.reportgenerator_status = reportgenerator_status
        
class LossRunFact(Base):
    __tablename__ = 'lossrun_fact'

    fact_id = Column(Integer, primary_key = True)
    loss_date = Column(Integer, ForeignKey('time_dim.timeid'))
    policy_id = Column(Integer, ForeignKey('policy_dim.policy_id'))
    loss_reported_date = Column(Integer, ForeignKey('time_dim.timeid'))
    claim_reference = Column(String)
    status_id = Column(Integer, ForeignKey('status_dim.status_id'))
    claimant_name = Column(String)
    expense_reserve = Column(Numeric)
    indemnity_reserve = Column(Numeric)
    expense_paid = Column(Numeric)
    indemnity_paid = Column(Numeric)
    total_incurred = Column(Numeric)
    lossrunreport_id = Column(Integer, ForeignKey('lossrunreport_dim.lossrunreport_id'))
    reportgenerator_id = Column(Integer, ForeignKey('reportgenerator_dim.reportgenerator_id'))
    insurer_id = Column(Integer, ForeignKey('insurer_dim.insurer_id'))
    insured_id = Column(Integer, ForeignKey('insured_dim.insured_id'))

    timeDim = relationship('TimeDim', foreign_keys=[loss_date])

    def __init__(self, fact_id, loss_date, policy_id, loss_reported_date, claim_reference, status_id, claimant_name, 
        expense_reserve, indemnity_reserve, expense_paid, indemnity_paid, total_incurred, lossrunreport_id, 
        reportgenerator_id, insurer_id, insured_id):
        self.fact_id = fact_id
        self.loss_date = loss_date
        self.policy_id = policy_id
        self.loss_reported_date = loss_reported_date
        self.claim_reference = claim_reference
        self.status_id = status_id
        self.claimant_name = claimant_name
        self.expense_reserve = expense_reserve
        self.indemnity_reserve = indemnity_reserve
        self.expense_paid = expense_paid
        self.indemnity_paid = indemnity_paid
        self.total_incurred = total_incurred
        self.lossrunreport_id = lossrunreport_id
        self.reportgenerator_id = reportgenerator_id
        self.insurer_id = insurer_id
        self.insured_id = insured_id

# Create tables on db
Base.metadata.create_all(engine)

# Create random records for db
timeDim = TimeDim(4, 9, 2020)
statusDim = StatusDim('Active')
insurerDim = InsurerDim('Insurer Company', 'Address Company', 'Reported')
insuredDim = InsuredDim('Insured Person', 'Address Person', 'Waiting')
policyDim = PolicyDim(1, 1, 1234, datetime.datetime.now(), datetime.datetime.now(), 'status')
lossRunReportDim = LossRunReportDim(datetime.datetime.now(), datetime.datetime.now())
reportGeneratorDim = ReportGeneratorDim('Report insure', 'Reporter address', 'pending')

fact = LossRunFact(2, 2, 2, 2, 'Claimant Person', 2, 'Claimant Name', 12.2, 123.25, 89.36, 125.3, 78.3, 2, 2, 2, 2)

Session.add(timeDim)
Session.add(statusDim)
Session.add(insurerDim)
Session.add(insuredDim)
Session.add(policyDim)
Session.add(lossRunReportDim)
Session.add(reportGeneratorDim)
Session.add(fact)
Session.commit()
