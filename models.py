from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AdvDec(Base):
    """ data model for advance decline numbers """
    __tablename__ = "adv_dec"
    date = Column("date", Date, primary_key=True, nullable=False)
    advance = Column("advance", Integer, nullable=False)
    decline = Column("decline", Integer, nullable=False)


class StockData(Base):
    """ Data model for stock data insertion """
    __tablename__ = "stock_data"
    id = Column(Integer,
                primary_key=True,
                nullable=False,
                autoincrement=True)
    stock_name = Column("stock_name", String(100),
                        nullable=False, index=True)
    date = Column("date", Date, ForeignKey(AdvDec.date), nullable=False, index=True)
    open = Column("open", Float, nullable=False)
    high = Column("high", Float, nullable=False)
    low = Column("low", Float, nullable=False)
    close = Column("Close", Float, nullable=False)
    del_volume = Column("del_volume", Integer, nullable=False)
    trade_volume = Column("trade_volume", Integer, nullable=False)
    adv_dec = relationship("AdvDec", cascade="all,delete", backref="stock_data")
