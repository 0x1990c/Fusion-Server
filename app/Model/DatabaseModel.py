from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = 'tbl_message'

    id = Column(Integer, primary_key=True)
    message_status = Column(Integer)
    categories = Column(JSON)
    phone_numbers = Column(JSON)
    last_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    qued_timestamp = Column(DateTime)
    sent_timestamp = Column(DateTime)
    sent_success = Column(Integer)
    image_url = Column(String(255))
    num_sent = Column(Integer)
    

class Project(Base):
    __tablename__ = 'tbl_project'

    id = Column(Integer, primary_key=True)
    claim_number = Column(String(255))
    customer_id = Column(Integer, ForeignKey('tbl_customer.id'))
    project_name = Column(String(255))
    last_message = Column(Text)
    message_status = Column(Integer)
    qued_timestamp = Column(DateTime)
    sent_timestamp = Column(DateTime)
    phone_sent_success = Column(Boolean)
    email_sent_success = Column(Boolean)

class MessageHistory(Base):
    __tablename__ = 'tbl_message_history'

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    project_id = Column(Integer)
    sent_time = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = 'tbl_report'    

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('tbl_project.id'))
    message = Column(Text)
    timestamp = Column(String(255))

class User(Base):
    __tablename__ = 'tbl_user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    forgot_password_token = Column(String(255))
    approved = Column(Integer)
    user_type = Column(Integer, default = 0)
    sms_balance = Column(Integer, default = 0)

class Variables(Base):
    __tablename__ = 'tbl_variables'

    id = Column(Integer, primary_key=True)
    openAIKey = Column(String(255))
    twilioPhoneNumber = Column(String(255))
    twilioAccountSID = Column(String(255))
    twilioAuthToken = Column(String(255))
    sendgridEmail = Column(String(255))
    sendgridApiKey = Column(String(255))
    optin_message = Column(Text)
    timer = Column(Integer)

class Status(Base):
    __tablename__ = 'tbl_status'

    id = Column(Integer, primary_key=True)
    db_update_status = Column(Integer)
    buildertrend_total = Column(Integer)
    buildertrend_current = Column(Integer)
    xactanalysis_total = Column(Integer)
    xactanalysis_current = Column(Integer)
    project_total = Column(Integer)
    project_current = Column(Integer)

class Customer(Base):
    __tablename__ = 'tbl_customer'

    id = Column(Integer, primary_key=True)
    phone_numbers = Column(JSON)
    categories = Column(JSON)


class CustomerCategory(Base):
    __tablename__ = 'tbl_customer_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class Phone(Base):
    __tablename__ = 'tbl_phone'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20))
    customer_id = Column(Integer, ForeignKey('tbl_customer.id'))
    opt_in_status = Column(Integer, ForeignKey('tbl_customer_category.id'))
    sent_timestamp = Column(DateTime)
    back_timestamp = Column(DateTime)
    
class Case(Base):
    __tablename__ = 'odyssey_cases'

    id = Column(Integer, primary_key=True)
    CaseCategoryKey = Column(String(255))
    CaseCategoryGroup = Column(String(255))
    CaseNumber = Column(String(255))
    Court = Column(String(255))
    CourtCode = Column(String(255))
    IsAppellateCourt = Column(String(255))
    FileDate = Column(DateTime)
    CaseStatus = Column(String(255))
    CaseStatusDate = Column(String(255))
    CaseType = Column(String(255))
    CaseSubType = Column(String(255))
    Style = Column(String(255))
    IsActive = Column(String(255))
    IsPublic = Column(String(255))
    AppearByDate = Column(String(255))
    BondAmount = Column(String(255))
    BondNumber = Column(String(255))
    BondStatus = Column(String(255))
    DefendantName = Column(String(255))
    DefendantAddress = Column(String(255))
    DefendantAddressCity = Column(String(255))
    DefendantAddressState = Column(String(255))
    DefendantAddressZip = Column(String(255))
    DefendantAddressZip4 = Column(String(255))
    PartyName1 = Column(String(255))
    PartyConnectionType1 = Column(String(255))
    PartyConnectionKey1 = Column(String(255))
    PartyAddress1 = Column(String(255))
    PartyName2 = Column(String(255))
    PartyConnectionType2 = Column(String(255))
    PartyConnectionKey2 = Column(String(255))
    PartyAddress2 = Column(String(255))
    PartyName3 = Column(String(255))
    PartyConnectionType3 = Column(String(255))
    PartyConnectionKey3 = Column(String(255))
    PartyAddress3 = Column(String(255))
    PartyName4 = Column(String(255))
    PartyConnectionType4 = Column(String(255))
    PartyConnectionKey4 = Column(String(255))
    PartyAddress4 = Column(String(255))
    PartyName5 = Column(String(255))
    PartyConnectionType5 = Column(String(255))
    PartyConnectionKey5 = Column(String(255))
    PartyAddress5 = Column(String(255))
    OtherParties = Column(Text)
    OffenseDate1 = Column(String(255))
    OffenseStatute1 = Column(String(255))
    OffenseDescription1 = Column(String(255))
    OffenseDegree1 = Column(String(255))
    OffenseDate2 = Column(String(255))
    OffenseStatute2 = Column(String(255))
    OffenseDescription2 = Column(String(255))
    OffenseDegree2 = Column(String(255))
    OffenseDate3 = Column(String(255))
    OffenseStatute3 = Column(String(255))
    OffenseDescription3 = Column(String(255))
    OffenseDegree3 = Column(String(255))
    OffenseDate4 = Column(String(255))
    OffenseStatute4 = Column(String(255))
    OffenseDescription4 = Column(String(255))
    OffenseDegree4 = Column(String(255))
    OffenseDate5 = Column(String(255))
    OffenseStatute5 = Column(String(255))
    OffenseDescription5 = Column(String(255))
    OffenseDegree5 = Column(String(255))
    OtherOffenses = Column(Text)
    EventDate1 = Column(String(255))
    EventType1 = Column(String(255))
    EventDescription1 = Column(String(255))
    EventDate2 = Column(String(255))
    EventType2 = Column(String(255))
    EventDescription2 = Column(String(255))
    EventDate3 = Column(String(255))
    EventType3 = Column(String(255))
    EventDescription3 = Column(String(255))
    EventDate4 = Column(String(255))
    EventType4 = Column(String(255))
    EventDescription4 = Column(String(255))
    EventDate5 = Column(String(255))
    EventType5 = Column(String(255))
    EventDescription5 = Column(String(255))
    OtherEvents = Column(Text)