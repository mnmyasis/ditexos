from sqlalchemy import text, Integer, String, Float, func, case
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import MetaData
from sqlalchemy import and_
from sqlalchemy.orm import Session
import os


class NewReport:

    def __init__(self, agency_client_id: int, start_date: str, end_date: str):
        self.engine = create_engine(
            (f"postgresql+psycopg2://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}"
             f"@{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}"),
            echo=True, pool_size=6, max_overflow=10
        )
        self.agency_client_id = agency_client_id
        self.start_date = start_date
        self.end_date = end_date
        self.session: Session = None

    def __get_table_cabinet(self):
        metadata_obj = MetaData()
        table = Table(
            'cabinets',
            metadata_obj,
            Column('agency_client_id', Integer),
            Column('source', String),
            Column('source_name', String),
            Column('is_brand', String),
            Column('campaign', String),
            Column('channel', String),
            Column('channel_name', String),
            Column('cost_', Float),
            Column('clicks', Integer),
            Column('impressions', Integer),
            Column('date', Integer),
        )
        return table

    def __get_table_amo(self):
        metadata_obj = MetaData()
        table = Table(
            'amo_kpf',
            metadata_obj,
            Column('agency_client_id', Integer),
            Column('utm_source', String),
            Column('channel', String),
            Column('utm_campaign', String),
            Column('lead_type', String),
            Column('is_brand', String),
            Column('date', Integer),
        )
        return table

    def get_leads(self, lead_type: str, is_brand: bool, cab: Table):
        amo = self.__get_table_amo()
        leads = self.session.query(
            func.count('*')
        ).filter(
            amo.c.agency_client_id == cab.c.agency_client_id,
            amo.c.lead_type == lead_type,
            amo.c.channel == cab.c.channel,
            amo.c.utm_source == cab.c.source,
            amo.c.is_brand == is_brand,
            amo.c.date.between(self.start_date, self.end_date)
        ).label(lead_type)
        return leads

    def get_cab(self, is_brand: bool, is_main: bool, directions: list, direction: str):
        cabinet = self.__get_table_cabinet()
        sources = ['yandex', 'google']
        channel = case((and_(cabinet.c.source == 'yandex', cabinet.c.channel == None), 'search'),
                       else_=cabinet.c.channel).label('channel')
        cabinet_aggr = [
            func.sum(cabinet.c.cost_).label('cost_'),
            func.sum(cabinet.c.clicks).label('clicks'),
            func.sum(cabinet.c.impressions).label('impressions'),
            cabinet.c.agency_client_id,
            cabinet.c.source,
            cabinet.c.channel_name,
            channel,
            cabinet.c.source_name,
        ]
        where_args = [
            cabinet.c.agency_client_id == self.agency_client_id,
            cabinet.c.is_brand == is_brand,
            cabinet.c.date.between(self.start_date, self.end_date),
            cabinet.c.source.in_(sources),
        ]
        if is_main:
            for direction_ in directions:
                where_args.append(cabinet.c.campaign.notlike(f'%{direction_}%'))
        else:
            where_args.append(cabinet.c.campaign.like(f'%{direction}%'))

        cab_sub = self.session.query(*cabinet_aggr).where(*where_args).group_by(
            cabinet.c.agency_client_id,
            cabinet.c.source,
            cabinet.c.source_name,
            cabinet.c.channel,
            cabinet.c.channel_name).subquery()

        leads = self.get_leads(
            lead_type='leads',
            is_brand=is_brand,
            cab=cab_sub,
        )
        kpf = self.get_leads(
            lead_type='kpf',
            is_brand=is_brand,
            cab=cab_sub,
        )
        cab = self.session.query(
            func.sum(cab_sub.c.cost_).label('cost_'),
            func.sum(cab_sub.c.clicks).label('clicks'),
            func.sum(cab_sub.c.impressions).label('impressions'),
            cab_sub.c.agency_client_id,
            (cab_sub.c.source_name + cab_sub.c.channel_name).label('source'),
            leads,
            kpf,
        ).group_by(
            cab_sub.c.agency_client_id,
            cab_sub.c.source,
            cab_sub.c.source_name,
            cab_sub.c.channel,
            cab_sub.c.channel_name
        ).subquery()

        cab_ = self.session.query(
            cab.c.source,
            func.round(cab.c.cost_, 2).label('cost_'),
            cab.c.impressions,
            cab.c.clicks,
            cab.c.leads,
            cab.c.kpf,
            func.round((cab.c.clicks / cab.c.impressions * 100), 2).label('ctr'),
            func.round((cab.c.cost_ / cab.c.clicks), 2).label('cpc'),
            func.round((cab.c.leads / cab.c.clicks * 100), 2).label('cr'),
            func.round((cab.c.cost_ / case((cab.c.leads == 0, 1), else_=cab.c.leads)), 2).label('cpl'),
            func.round((cab.c.cost_ / case((cab.c.kpf == 0, 1), else_=cab.c.kpf)), 2).label('kpf_cpl'),
        )
        return cab_

    def get(self, direction: str, directions: list, is_main: bool, is_brand: bool):
        self.session = Session(bind=self.engine)
        cab = self.get_cab(
            is_brand=is_brand,
            directions=directions,
            is_main=is_main,
            direction=direction
        )
        return cab


if __name__ == '__main__':
    directions = ['kazahstan']
    new_report = NewReport(
        start_date='2022-02-01',
        end_date='2022-02-28',
        agency_client_id=12
    )
    for dir_ in directions:
        new_report.get(direction=dir_, directions=directions, is_brand=False, is_main=True)
