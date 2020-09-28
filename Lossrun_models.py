from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
import datetime

engine = create_engine('postgresql://postgres:password@localhost/lossrun', echo=True)
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

    @validates('day', 'month', 'year')
    def validate_timeDim(self, key, field):
        if field is None:
            return None
        if not isinstance(field, int):
            raise AssertionError(key + ' must be an integer')
        return field

class StatusDim(Base):
    __tablename__ = 'status_dim'

    status_id = Column(Integer, primary_key = True)
    status_name = Column(String)

    def __init__(self, status_name):
        self.status_name = status_name

class InsurerDim(Base):
    __tablename__ = 'insurer_dim'

    insurer_id = Column(Integer, primary_key = True)
    insurer_name = Column(String)
    insurer_address = Column(String)
    insurer_status = Column(String)

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

    def __init__(self, insured_id, insurer_id, policy_number, policy_start_date, policy_end_date, policy_status):
        self.insured_id = insured_id
        self.insurer_id = insurer_id
        self.policy_number = policy_number
        self.policy_start_date = policy_start_date
        self.policy_end_date = policy_end_date
        self.policy_status = policy_status

    @validates('insured_id', 'insurer_id', 'policy_number')
    def validate_policyDim(self, key, field):
        if field is None:
            return None
        if not isinstance(field, int):
            raise AssertionError(key + ' must be an integer')
        return field

class LossRunReportDim(Base):
    __tablename__ = 'lossrunreport_dim'

    lossrunreport_id = Column(Integer, primary_key = True)
    lossrunreport_load_date = Column(DateTime)
    lossrunreport_date = Column(DateTime)

    def __init__(self, lossrunreport_load_date, lossrunreport_date):
        self.lossrunreport_load_date = lossrunreport_load_date
        self.lossrunreport_date = lossrunreport_date

class ReportGeneratorDim(Base):
    __tablename__ = 'reportgenerator_dim'

    reportgenerator_id = Column(Integer, primary_key = True)
    reportgenerator_name = Column(String)
    reportgenerator_address = Column(String)
    reportgenerator_status = Column(String)

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
    PolicyDim = relationship('PolicyDim', foreign_keys=[policy_id])
    reportedDate = relationship('TimeDim', foreign_keys=[loss_reported_date])
    statusDim = relationship('StatusDim', foreign_keys=[status_id])
    lossRunReportDim = relationship('LossRunReportDim', foreign_keys=[lossrunreport_id])
    reportGeneratorDim = relationship('ReportGeneratorDim', foreign_keys=[reportgenerator_id])
    insurerDim = relationship('InsurerDim', foreign_keys=[insurer_id])
    insuredDim = relationship('InsuredDim', foreign_keys=[insured_id])

    @validates('loss_date', 'policy_id', 'loss_reported_date', 'status_id', 'lossrunreport_id', 'reportgenerator_id', 'insurer_id', 'insured_id')
    def validate_lossRunFactIds(self, key, field):
        if field is None:
            return None
        if not isinstance(field, int):
            raise AssertionError(key + ' must be an integer')
        return field

    def __init__(self, loss_date, policy_id, loss_reported_date, claim_reference, status_id, claimant_name, 
        expense_reserve, indemnity_reserve, expense_paid, indemnity_paid, total_incurred, lossrunreport_id, 
        reportgenerator_id, insurer_id, insured_id):
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

Base.metadata.create_all(engine)

def registerRecord(**kwargs):
    emptyArgs = { 'timeDimDay': None, 'timeDimMonth': None, 'timeDimYear': None, 'statusDim': None, 'insurerDimName': None, 'insurerDimAddress': None, 
    'insurerDimStatus': None, 'insuredDimName': None, 'insuredDimAddress': None, 'insuredDimStatus': None, 'policyDimInsuredId': None, 
    'policyDimInsurerId': None, 'policy_number': None, 'statusName': None, 'policyDimStartDate': None, 'policyDimEndDate': None, 'expenseReserve': None, 'claimantName': None, 'policyDimStatus': None, 'lossRunReportDimLoadDate': None, 
    'lossRunReportDimDate': None, 'reportGeneratorDimName': None, 'reportGeneratorDimAddress': None, 'reportGeneratorDimStatus': None, 'claimReference': None, 'indemnityReserve': None, 'expensePaid': None, 'indemnityPaid': None,
    'totalIncurred': None }
    completeArgs = {**emptyArgs, **kwargs}
    register(completeArgs)

def register(data):
    timeDim = validateData(TimeDim, 'timeid', data['timeDimDay'], data['timeDimMonth'], data['timeDimYear'])
    statusDim = validateData(StatusDim, 'status_id', data['statusName'])
    insurerDim = validateData(InsurerDim, 'insurer_id', data['insurerDimName'], data['insurerDimAddress'], data['insurerDimStatus'])
    insuredDim = validateData(InsuredDim, 'insured_id', data['insuredDimName'], data['insuredDimAddress'], data['insuredDimStatus'])
    policyDim = validateData(PolicyDim, 'policy_id', data['policyDimInsuredId'], data['policyDimInsurerId'], data['policy_number'], data['policyDimStartDate'], data['policyDimEndDate'], data['policyDimStatus'])
    lossRunReportDim = validateData(LossRunReportDim, 'lossrunreport_id', data['lossRunReportDimLoadDate'], data['lossRunReportDimDate'])
    reportGeneratorDim = validateData(ReportGeneratorDim, 'reportgenerator_id', data['reportGeneratorDimName'], data['reportGeneratorDimAddress'], data['reportGeneratorDimStatus'])
    fact = LossRunFact(timeDim, policyDim, timeDim, data['claimReference'], statusDim, data['claimantName'], data['expenseReserve'], data['indemnityReserve'], data['expensePaid'], data['indemnityPaid'], data['totalIncurred'], lossRunReportDim, reportGeneratorDim, insurerDim, insuredDim)
    Session.add(fact)
    Session.commit()

def validateData(objectClass, id_name, *args):
    if all(value is None for value in args):
        return None
    else:
        dataObject = objectClass(*args)
        Session.add(dataObject)
        Session.flush()
        return getattr(dataObject, id_name)

<<<<<<< HEAD
Base.metadata.create_all(engine)

registerRecord(timeDimDay = 12, timeDimMonth = 9, timeDimYear = 20, policyDimStartDate = datetime.datetime.now(), policyDimStatus = "Test", 
    reportGeneratorDimName = "Report generator", insuredDimName = "Insured Name",  insurerDimName = "test", statusName = "fasdfdsa", 
    lossRunReportDimDate = datetime.datetime.now())    
=======
registerRecord(timeDimDay = 5, timeDimMonth = 12, statusName = 'Test') 
>>>>>>> 8c53cc267759ef19f8b0db7be1e5f9cc51d377cb
