from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    property_address = Column(String(500), nullable=True, index=True)
    anthropic_input_tokens = Column(Integer, default=0)
    anthropic_output_tokens = Column(Integer, default=0)
    openai_input_tokens = Column(Integer, default=0)
    openai_output_tokens = Column(Integer, default=0)
    anthropic_cost_usd = Column(Numeric(10, 6), default=0)
    openai_cost_usd = Column(Numeric(10, 6), default=0)
    total_cost_usd = Column(Numeric(10, 6), default=0)
    summary_text = Column(Text, nullable=True)
