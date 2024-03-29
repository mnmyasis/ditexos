from typing import List, Dict, Tuple

from django.db.models import QuerySet

from .models import *
import pandas as pd
from django.db import connection


class ReportsQuerySet(models.QuerySet):

    def _dictfetchall(self, cursor):
        """Returns all rows from a cursor as a dict"""
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def get_clients_report(self, user_id):
        cursor = connection.cursor()
        sql = """
            select
                   ag_cl.id pk,
                   ag_cl.name,
                   comagic.leads,
                   yandex.ya_cost yandex_cost,
                   round(google.go_cost, 2) google_cost
            from agency_clients ag_cl
            left join (
                select co_api.agency_client_id, count(*) leads from comagic_api_token co_api
                join comagic_report cr on co_api.id = cr.api_client_id
                where cr.utm_source='yandex' or cr.utm_source='google'
                group by co_api.id
                ) comagic on ag_cl.id = comagic.agency_client_id
            left join (
                select id, agency_client_name, sum(cost_) ya_cost from yandex_report_view
                group by id, agency_client_name
            ) yandex on yandex.id = ag_cl.id
            left join (
                select id, sum(cost_) as go_cost
                from google_report_view
                group by id
                ) google on ag_cl.id = google.id
            where ag_cl.user_id = {}
             """.format(user_id)
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_report_client_cabinet(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select source,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, source
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_channel(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select source,
                   channel,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, source, channel
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_campaign(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select source,
                   agency_client_id,
                   campaign,
                   campaign_id,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, source, campaign, campaign_id
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_direction(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   direction,
                   date,
                   round(sum(cost_), 2) cost_,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, date, direction
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        if report:
            df = pd.DataFrame(report)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df_cost = df.pivot_table(index=['date'], columns=['direction'], values='cost_', aggfunc='sum')
            df_leads = df.pivot_table(index=['date'], columns=['direction'], values='leads', aggfunc='sum')
            df_leads = df_leads.to_json(orient="split", date_format='iso')
            df_cost = df_cost.to_json(orient="split", date_format='iso')
            df_cost = json.loads(df_cost)
            df_leads = json.loads(df_leads)
            cost_and_leads = []
            for d_cost, d_leads in zip(df_cost['data'], df_leads['data']):
                cost_and_leads.append(zip(d_cost, d_leads))
            df_cost['context'] = zip(df_cost['index'], cost_and_leads)
            return df_cost
        else:
            return None

    def get_direction_for_export(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   direction,
                   date,
                   round(sum(cost_), 2) cost_,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, date, direction
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        if report:
            df = pd.DataFrame(report)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df_direction = df.pivot_table(index=['date'], columns=['direction'], values=['cost_', 'leads'],
                                          aggfunc='sum')
            return df_direction.swaplevel(0, 1, axis=1).sort_index(axis=1)
        else:
            return None

    def get_client_period_campaign(self, agency_client_id, p1_start_date, p1_end_date, p2_start_date, p2_end_date):
        p1 = '{} - {}'.format(p1_start_date, p1_end_date)
        p2 = '{} - {}'.format(p2_start_date, p2_end_date)
        cursor = connection.cursor()
        sql = f"""
            select
                period_1.p1,
                period_2.p2,
                period_1.campaign,
                period_1.cost_ p1_cost_,
                period_2.cost_ p2_cost_,
                period_1.impressions p1_impressions,
                period_2.impressions p2_impressions,
                period_1.clicks p1_clicks,
                period_2.clicks p2_clicks,
                period_1.ctr p1_ctr,
                period_2.ctr p2_ctr,
                period_1.cpc p1_cpc,
                period_2.cpc p2_cpc,
                period_1.cr p1_cr,
                period_2.cr p2_cr,
                period_1.cpl p1_cpl,
                period_2.cpl p2_cpl,
                period_1.leads p1_leads,
                period_2.leads p2_leads,
                round((period_1.cost_ -
                case
                    when period_2.cost_ = 0 then 1
                    else period_2.cost_
                end) /
                case
                    when period_1.cost_ = 0 then 1
                    else period_1.cost_
                end * 100, 2) change_cost_,
                round((period_1.impressions -
                case
                    when period_2.impressions = 0 then 1
                    else period_2.impressions
                end) /
                case
                    when period_1.impressions = 0 then 1
                    else period_1.impressions
                end * 100, 2) change_impressions,
                round((period_1.clicks -
                case
                    when period_2.clicks = 0 then 1
                    else period_2.clicks
                end) /
                case
                    when period_1.clicks = 0 then 1
                    else period_1.clicks
                end * 100, 2) change_clicks,
                period_1.ctr - period_2.ctr change_ctr,
                round((period_1.cpc -
                case
                    when period_2.cpc = 0 then 1
                    else period_2.cpc
                end) /
                case
                    when period_1.cpc = 0 then 1
                    else period_1.cpc
                end * 100, 2) change_cpc,
                period_1.cr - period_2.cr change_cr,
                round((period_1.cpl -
                case
                    when period_2.cpl = 0 then 1
                    else period_2.cpl
                end) /
                case
                    when period_1.cpl = 0 then 1
                    else period_1.cpl
                end * 100, 2) change_cpl,
                round((period_1.leads -
                case
                    when period_2.leads = 0 then 1
                    else period_2.leads
                end) /
                case
                    when period_1.leads = 0 then 1
                    else period_1.leads
                end * 100, 2) change_leads 
            from
            (
            select
                   '{p1}' p1,
                   campaign,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{p1_start_date}' and '{p1_end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, campaign
            ) period_1
                JOIN
            (select
                   '{p2}' p2,
                   campaign,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{p2_start_date}' and '{p2_end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, campaign
            ) period_2 on period_1.campaign = period_2.campaign
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_campaign_keyword(self, agency_client_id, source, campaign_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   key_word,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_keyword_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id} and
                  source = '{source}' and
                  campaign_id = '{campaign_id}'
            group by agency_client_id, key_word
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        sql = f"""
            select distinct campaign from cabinet_for_comagic_keyword_report where
              campaign_id = '{campaign_id}' and                                                                 
              agency_client_id = {agency_client_id} and
              source = '{source}'
            """
        cursor.execute(sql)
        campaign_name = cursor.fetchone()[0]
        return report, campaign_name

    def get_comagic_other_report(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   other_leads.agency_client_id,
                   other_leads.domain_,
                   case
                       when sum(other_leads.go_leads) is NULL then 0
                       else sum(other_leads.go_leads)
                   end go_leads,
                   case
                       when sum(other_leads.ya_leads) is NULL then 0
                       else sum(other_leads.ya_leads)
                   end ya_leads,
                   case
                       when sum(other_leads.other_leads) is NULL then 0
                       else sum(other_leads.other_leads)
                   end other_leads
            from (
                select
                       co_other.agency_client_id,
                       co_other.domain_,
                       co_other.source_type,
                       case
                           when co_other.campaign = 'Визитка Google' then count(co_other.campaign)
                       end go_leads,
                       case
                           when co_other.campaign = 'Визитка Яндекс' then count(co_other.campaign)
                       end ya_leads,
                       case
                           when co_other.source_type = 'other' then count(co_other.source_type)
                       end other_leads,
                       co_other.date
                from
                (
                select ag_cl.id agency_client_id,
                       cdr.site_domain_name domain_,
                       case
                           when cr.campaign_name = 'Визитка Googke' then 'Визитка Google'
                           else cr.campaign_name
                       end campaign,
                       cr.source_type,
                       cr.date
                from agency_clients ag_cl
                left join comagic_api_token co_api on ag_cl.id = co_api.agency_client_id
                left join comagic_report cr on co_api.id = cr.api_client_id
                left join comagic_domain_report cdr on cr.site_domain_name_id = cdr.id
                where cr.source_type in ('cutaways', 'other')
                ) co_other
                group by co_other.agency_client_id, co_other.domain_, co_other.source_type, co_other.campaign, co_other.date
            ) other_leads
            where other_leads.date between '{start_date}' and '{end_date}' and other_leads.agency_client_id = {agency_client_id}
            group by other_leads.agency_client_id, other_leads.domain_
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_project_channel(self, agency_client_id, project_tag, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select cnn.date,
                   cnn.source,
                   cnn.channel,
                   sum(cnn.impressions) impressions,
                   sum(cnn.clicks) clicks,
                   sum(cnn.ctr) ctr,
                   sum(cnn.cpc) cpc,
                   sum(cnn.cost_) cost_
            from (
            select
                   ads.id,
                   ads.date,
                   ads.source,
                   ads.campaign,
                   case
                       when campaign ~* '_search' THEN 'search'
                       when campaign ~* '_network' THEN 'network'
                   END channel,
                   ads.impressions,
                   ads.clicks,
                   round(ads.clicks /
                   case
                       when ads.impressions = 0 then 1
                       else ads.impressions
                   end * 100, 2) ctr,
                   round(ads.cost_ /
                   case
                       when ads.clicks = 0 then 1
                       else ads.clicks
                   end, 2) cpc,
                   ads.cost_
            from (
                    (select id,
                        'yandex' source,
                        campaign,
                        campaign_id,
                        sum(cost_) cost_,
                        sum(clicks) clicks,
                        sum(impressions) impressions,
                        date
                    from yandex_report_view
                    group by id, campaign, campaign_id, date)
                    union all
                    (select id,
                        'google' source,
                        campaign,
                        campaign_id,
                        sum(cost_) cost_,
                        sum(clicks) clicks,
                        sum(impressions) impressions,
                        date
                    from google_report_view
                    group by id, campaign, campaign_id, date)
                    )
                ads
                ) cnn where 
                    cnn.id = {agency_client_id} and
                    cnn.campaign ~* '{project_tag}' and
                    cnn.date between '{start_date}' and '{end_date}'
                group by cnn.date, cnn.source, cnn.channel
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def __direction_filter_for_brand(self, direction_name: str) -> Tuple[str, str]:
        """Генерирует фильтр выделения направления. Возвращает filter_campaign, filter_utm_campaign."""
        filter_utm_campaign = f"utm_campaign ~* '{direction_name}'"
        filter_campaign = f"campaign ~* '{direction_name}'"
        return filter_campaign, filter_utm_campaign

    def __diff_main_filter_for_brand(self, directions: QuerySet, is_brand: bool) -> Tuple[str, str]:
        """Генерирует исключающие фильтры для таблицы Общее. Возвращает filter_campaign, filter_utm_campaign."""
        if len(directions) == 1:  # Если нет необходимости выделять направление
            filter_campaign = "campaign ~* ''"
            filter_utm_campaign = "utm_campaign ~* ''"
        else:  # Исключение выделенных направлений из общей статистики
            select_directions = []
            for direction in directions:
                if direction.is_main is False:
                    if direction.only_one_type in ('br', 'all') and is_brand:
                        select_directions.append(direction.direction)
                    if direction.only_one_type in ('nb', 'all') and is_brand is False:
                        select_directions.append(direction.direction)
            filter_campaign = ' and '.join(
                [f"campaign !~* '{_dir}'" for _dir in select_directions]
            )
            filter_utm_campaign = ' and '.join(
                [f"utm_campaign !~* '{_dir}'" for _dir in select_directions]
            )
        return filter_campaign, filter_utm_campaign

    def __create_raw_sql_for_brand(self,
                                   is_brand: bool,
                                   agency_client_id: int,
                                   filter_campaign: str,
                                   filter_utm_campaign: str,
                                   start_date: str,
                                   end_date: str) -> str:
        """Собирает sql запрос."""
        sql = f"""
                    select br.agency_client_id,
               br.source,
               br.channel,
               br.source_name || br.channel_name t_source,
               round(br.cost_, 2)      cost_,
               br.impressions,
               br.clicks,
               br.leads,
               br.kpf,
               round(br.clicks /
                     case
                         when br.impressions = 0 then 1
                         else br.impressions
                         end * 100, 2) ctr,
               round(br.cost_ /
                     case
                         when br.clicks = 0 then 1
                         else br.clicks
                         end, 2)       cpc,
               round(br.leads /
                     case
                         when br.clicks = 0 then 1
                         else br.clicks
                         end * 100, 2) cr,
               round(br.cost_ /
                     case
                         when br.leads = 0 then 1
                         else br.leads
                         end, 2)       cpl,
               round(br.cost_ /
                     case
                         when br.kpf = 0 then 1
                         else br.kpf
                         end, 2)       kpf_cpl
        from (
                 select agency_client_id,
                        source,
                        source_name,
                        channel,
                        channel_name,
                        sum(cost_)                         cost_,
                        sum(impressions)                   impressions,
                        sum(clicks)                        clicks,
                        (select count(*)
                         from amo_kpf
                         where agency_client_id = {agency_client_id}
                           and date between '{start_date}' and '{end_date}'
                           and lead_type = 'leads'
                           and {filter_utm_campaign}
                           and is_brand = {is_brand}
                           and cabinets.source = utm_source
                           and cabinets.channel = channel) leads,
                        (select count(*)
                         from amo_kpf
                         where agency_client_id = {agency_client_id}
                           and date between '{start_date}' and '{end_date}'
                           and lead_type = 'kpf'
                           and {filter_utm_campaign}
                           and is_brand = {is_brand}
                           and cabinets.source = utm_source
                           and cabinets.channel = channel) kpf
                 from cabinets
                 where agency_client_id = {agency_client_id}
                   and date between '{start_date}' and '{end_date}'
                   and source in ('yandex', 'google')
                   and is_brand = {is_brand}
                   and {filter_campaign}
                 group by agency_client_id, source, source_name, channel, channel_name) br;
                """
        return sql

    def get_brand_nvm(self,
                      agency_client_id: int,
                      directions: QuerySet,
                      start_date: str,
                      end_date: str) -> List[Dict]:
        """Выгружает брендовые отчеты."""
        brands_types = (True, False)
        cursor = connection.cursor()
        brand_reports = []
        for direction in directions:
            for is_brand in brands_types:
                if direction.is_main:
                    filter_campaign, filter_utm_campaign = self.__diff_main_filter_for_brand(directions, is_brand)
                else:
                    filter_campaign, filter_utm_campaign = self.__direction_filter_for_brand(direction.direction)
                sql = self.__create_raw_sql_for_brand(is_brand=is_brand,
                                                      agency_client_id=agency_client_id,
                                                      filter_campaign=filter_campaign,
                                                      filter_utm_campaign=filter_utm_campaign,
                                                      start_date=start_date,
                                                      end_date=end_date)
                cursor.execute(sql)
                reports = {}
                if direction.only_one_type in ('br', 'all') and is_brand:
                    reports['brand_report'] = self._dictfetchall(cursor)
                if direction.only_one_type in ('nb', 'all') and is_brand is False:
                    reports['no_brand_report'] = self._dictfetchall(cursor)
                reports['direction_name'] = direction.name
                brand_reports.append(reports)
        return brand_reports

    def get_week_nvm(self, agency_client_id):
        cursor = connection.cursor()
        sql = f"""
            select *,
       round(wk.clicks /
             case
                 when wk.impressions = 0 then 1
                 else wk.impressions
                 end * 100, 2) ctr,
       round(wk.cost_ /
             case
                 when wk.clicks = 0 then 1
                 else wk.clicks
                 end, 2)       cpc,
       round(wk.leads /
             case
                 when wk.clicks = 0 then 1
                 else wk.clicks
                 end * 100, 2) cr,
       round(wk.gk /
             case
                 when wk.clicks = 0 then 1
                 else wk.clicks
                 end * 100, 2) gk_cr,
       round(wk.cost_ /
             case
                 when wk.leads = 0 then 1
                 else wk.leads
                 end, 2)       cpl,
       round(wk.cost_ /
             case
                 when wk.gk = 0 then 1
                 else wk.gk
                 end, 2)       gk_cpl
from (
         select agency_client_id,
                source,
                source_name,
                week,
                channel_name,
                source_name || channel_name          channel_,
                channel,
                sum(impressions)                     impressions,
                round(sum(cost_), 2)                 cost_,
                sum(clicks)                          clicks,
                (select count(*) leads
                 from amo_kpf
                 where agency_client_id = {agency_client_id}
                   and week = cabinets.week
                   and lead_type = 'leads'
                   and channel = cabinets.channel
                   and utm_source = cabinets.source) leads,
                (select count(*) leads
                 from amo_kpf
                 where agency_client_id = {agency_client_id}
                   and week = cabinets.week
                   and lead_type = 'gk'
                   and channel = cabinets.channel
                   and utm_source = cabinets.source) gk
         from cabinets
         where agency_client_id = {agency_client_id}
         group by agency_client_id, source, source_name, channel, channel_name, week
     ) wk
order by wk.week desc, wk.channel_;

        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_month_nvm(self, agency_client_id):
        cursor = connection.cursor()
        sql = f"""
            select amo_report.agency_client_id,
                   amo_report.month_,
                   amo_report.source,
                   case
                       when source = 'google' THEN 'Google Ads'
                       when source = 'yandex' THEN 'Яндекс Директ'
                       when source = 'vk_di' THEN 'Вконтакте'
                       when source = 'mytarget_di' THEN 'MyTarget'
                   END source_,
                   round(amo_report.cost_, 2) cost_,
                   amo_report.clicks,
                   amo_report.impressions,
                   amo_report.leads,
                   amo_report.gk,
                   round(amo_report.clicks /
                   case
                       when amo_report.impressions = 0 then 1
                       else amo_report.impressions
                   end * 100, 2) ctr,
                   round(amo_report.cost_ /
                   case
                       when amo_report.clicks = 0 then 1
                       else amo_report.clicks
                   end, 2) cpc,
                   round(amo_report.leads /
                   case
                       when amo_report.clicks = 0 then 1
                       else amo_report.clicks
                   end * 100, 2) cr,
                   round(amo_report.gk /
                   case
                       when amo_report.clicks = 0 then 1
                       else amo_report.clicks
                   end * 100, 2) gk_cr,
                   round(amo_report.cost_ /
                   case
                       when amo_report.leads = 0 then 1
                       else amo_report.leads
                   end, 2) cpl,
                   round(amo_report.cost_ /
                   case
                       when amo_report.gk = 0 then 1
                       else amo_report.gk
                   end, 2) gk_cpl

            from (
                select cab.agency_client_id,
                       cab.source,
                       cab.tmp_month,
                       cab.month_,
                       sum(cab.cost_) cost_,
                       sum(cab.clicks) clicks,
                       sum(cab.impressions) impressions,
                       sum(case when gk.leads is NULL then 0
                           else gk.leads
                       end) gk,
                       sum(case when lead.leads is NULL then 0
                           else lead.leads
                       end) leads
                from (
                    select
                       agency_client_id,
                       source,
                       sum(cost_) cost_,
                       sum(clicks) clicks,
                       sum(impressions) impressions,
                       date_trunc('month', date) tmp_month,
                       to_char(date_trunc('month', date), 'YYYY - MONTH') month_,
                       date
                    from cabinets
                    group by agency_client_id, source, date
                ) cab
                left join (
                    select
                           agency_client_id,
                           count(*) leads,
                           utm_source,
                           date
                    from amo_kpf where lead_type='gk'
                    group by agency_client_id, utm_source, date
                    ) gk on cab.source = gk.utm_source and
                             cab.date = gk.date and
                             cab.agency_client_id = gk.agency_client_id
                    left join (
                        select
                           agency_client_id,
                           count(*) leads,
                           utm_source,
                           date
                    from amo_kpf where lead_type='leads'
                    group by agency_client_id, utm_source, date
                    ) lead on cab.source = lead.utm_source and
                              cab.date = lead.date and
                              cab.agency_client_id = lead.agency_client_id
                where cab.agency_client_id = {agency_client_id} and month_ is not null
                group by cab.agency_client_id, cab.tmp_month, cab.month_, cab.source
            ) amo_report order by tmp_month DESC;
        """
        sql = f"""
            select *,
       round(m.clicks /
             case
                 when m.impressions = 0 then 1
                 else m.impressions
                 end * 100, 2) ctr,
       round(m.cost_ /
             case
                 when m.clicks = 0 then 1
                 else m.clicks
                 end, 2)       cpc,
       round(m.leads /
             case
                 when m.clicks = 0 then 1
                 else m.clicks
                 end * 100, 2) cr,
       round(m.gk /
             case
                 when m.clicks = 0 then 1
                 else m.clicks
                 end * 100, 2) gk_cr,
       round(m.cost_ /
             case
                 when m.leads = 0 then 1
                 else m.leads
                 end, 2)       cpl,
       round(m.cost_ /
             case
                 when m.gk = 0 then 1
                 else m.gk
                 end, 2)       gk_cpl
from (
         select agency_client_id,
                source,
                month_string,
                source_name,
                sum(impressions)     impressions,
                round(sum(cost_), 2) cost_,
                sum(clicks)          clicks,
                month_,
                (
                    select count(*)
                    from amo_kpf
                    where agency_client_id = {agency_client_id}
                      and lead_type = 'leads'
                      and cabinets.source = utm_source
                      and cabinets.month_ = month_
                )                    leads,
                (
                    select count(*)
                    from amo_kpf
                    where agency_client_id = {agency_client_id}
                      and lead_type = 'gk'
                      and cabinets.source = utm_source
                      and cabinets.month_ = month_
                )                    gk
         from cabinets
         where agency_client_id = {agency_client_id}
         group by agency_client_id, source, source_name, month_, month_string
         order by month_ desc) m;
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_campaign_nvm(self, agency_client_id):
        cursor = connection.cursor()
        sql = f"""
                    select amo_report.month_,
                               amo_report.agency_client_id,
                               amo_report.month_string,
                               amo_report.source,
                               case
                                   when source = 'google' THEN 'Google Ads'
                                   when source = 'yandex' THEN 'Яндекс Директ'
                                   when source = 'vk_di' THEN 'Вконтакте'
                                   when source = 'mytarget_di' THEN 'MyTarget'
                               END source_,
                               amo_report.campaign,
                               round(amo_report.cost_, 2) cost_,
                               amo_report.clicks,
                               amo_report.impressions,
                               amo_report.leads,
                               amo_report.gk,
                               round(amo_report.clicks /
                               case
                                   when amo_report.impressions = 0 then 1
                                   else amo_report.impressions
                               end * 100, 2) ctr,
                               round(amo_report.cost_ /
                               case
                                   when amo_report.clicks = 0 then 1
                                   else amo_report.clicks
                               end, 2) cpc,
                               round(amo_report.leads /
                               case
                                   when amo_report.clicks = 0 then 1
                                   else amo_report.clicks
                               end * 100, 2) cr,
                               round(amo_report.gk /
                               case
                                   when amo_report.clicks = 0 then 1
                                   else amo_report.clicks
                               end * 100, 2) gk_cr,
                               round(amo_report.cost_ /
                               case
                                   when amo_report.leads = 0 then 1
                                   else amo_report.leads
                               end, 2) cpl,
                               round(amo_report.cost_ /
                               case
                                   when amo_report.gk = 0 then 1
                                   else amo_report.gk
                               end, 2) gk_cpl

                        from (
                            select cab.agency_client_id,
                                   cab.source,
                                   cab.campaign,
                                   cab.month_string,
                                   cab.month_,
                                   sum(cab.cost_) cost_,
                                   sum(cab.clicks) clicks,
                                   sum(cab.impressions) impressions,
                                   sum(case when gk.leads is NULL then 0
                                       else gk.leads
                                   end) gk,
                                   sum(case when lead.leads is NULL then 0
                                       else lead.leads
                                   end) leads
                            from (
                                select
                                   agency_client_id,
                                   source,
                                   campaign,
                                   sum(cost_) cost_,
                                   sum(clicks) clicks,
                                   sum(impressions) impressions,
                                   month_,
                                   month_string
                                from cabinets
                                where agency_client_id={agency_client_id} and date is not null
                                group by agency_client_id, source, campaign, month_, month_string
                            ) cab

                            left join (
                                select
                                       agency_client_id,
                                       count(*) leads,
                                       utm_source,
                                       case
                                           when utm_campaign ~* 'yuzhnaya_stolica_kviz_krd_search' THEN 'yuzhnaya_stolica_kviz_krd_brand_search'
                                           when utm_campaign ~* 'zolotoj_gorod_kviz_rf_search' THEN 'zolotoj_gorod_kviz_krd_brand_search'
                                           when utm_campaign ~* 'perfomance_max' THEN 'performance_max'
                                           when utm_campaign is null and utm_source = 'yandex' THEN 'yandex_cutaway'
                                           when utm_campaign is null and utm_source = 'google' THEN 'google_cutaway'
                                           else utm_campaign
                                       END utm_campaign,
                                       month_
                                from amo_kpf where lead_type='gk'
                                group by agency_client_id, utm_source, utm_campaign, month_
                                ) gk on cab.source = gk.utm_source and
                                        cab.campaign = gk.utm_campaign and
                                        cab.month_ = gk.month_ and
                                        cab.agency_client_id = gk.agency_client_id
                                left join (
                                    select
                                       agency_client_id,
                                       count(*) leads,
                                       utm_source,
                                       case
                                           when utm_campaign ~* 'yuzhnaya_stolica_kviz_krd_search' THEN 'yuzhnaya_stolica_kviz_krd_brand_search'
                                           when utm_campaign ~* 'zolotoj_gorod_kviz_rf_search' THEN 'zolotoj_gorod_kviz_krd_brand_search'
                                           when utm_campaign ~* 'perfomance_max' THEN 'performance_max'
                                           when utm_campaign is null and utm_source = 'yandex' THEN 'yandex_cutaway'
                                           when utm_campaign is null and utm_source = 'google' THEN 'google_cutaway'
                                           else utm_campaign
                                       END utm_campaign,
                                       month_
                                from amo_kpf where lead_type='leads'
                                group by agency_client_id, utm_source, utm_campaign, month_
                                ) lead on cab.source = lead.utm_source and
                                          cab.campaign = lead.utm_campaign and
                                          cab.month_ = lead.month_ and
                                          cab.agency_client_id = lead.agency_client_id
                            where cab.agency_client_id = {agency_client_id}
                            group by cab.agency_client_id, cab.source, cab.campaign, cab.month_, cab.month_string
                            union
                            (select leads.agency_client_id,
                                    leads.source,
                                    leads.campaign,
                                    month_string,
                                    month_,
                                    0 clicks,
                                    0 impressions,
                                    0 cost_,
                                    sum(case
                                        when leads.gk is null then 0
                                        else leads.gk
                                    end) gk,
                                    sum(case
                                        when leads.leads is null then 0
                                        else leads.leads
                                    end) leads
                                    from (select
                                       agency_client_id,
                                       utm_source as source,
                                       case
                                           when utm_campaign is null and utm_source = 'yandex' THEN 'yandex_cutaway'
                                           when utm_campaign is null and utm_source = 'google' THEN 'google_cutaway'
                                           else utm_campaign
                                       END campaign,
                                       case
                                           when lead_type = 'leads' THEN count(lead_type)
                                       end leads,
                                       case
                                           when lead_type = 'gk' THEN count(lead_type)
                                       end gk,
                                       month_,
                                       month_string
                                from amo_kpf where
                                    utm_campaign is null and
                                    utm_source in ('google', 'yandex') and
                                    agency_client_id = {agency_client_id}
                                group by agency_client_id, lead_type, utm_source, source, utm_campaign, campaign, month_, month_string) leads
                                group by leads.agency_client_id, leads.source, leads.campaign, month_string, month_

                            )
                        ) amo_report order by month_ DESC, source ASC;
                """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_target_nvm(self, agency_client_id: int, start_date: str, end_date: str):
        cursor = connection.cursor()
        sql = f"""
            select
                    cab.agency_client_id agency_client_id,
                    cab.source source,
                    cab.cost_ cost_,
                    cab.impressions impressions,
                    cab.clicks clicks,
                    case
                       when kpf.leads isnull Then 0
                       else kpf.leads
                    end kpf,
                    lead.leads leads,
                   round(cab.clicks /
                   case
                       when cab.impressions = 0 then 1
                       else cab.impressions
                   end * 100, 2) ctr,
                   round(cab.cost_ /
                   case
                       when cab.clicks = 0 then 1
                       else cab.clicks
                   end, 2) cpc,
                   round(lead.leads /
                   case
                       when cab.clicks = 0 then 1
                       else cab.clicks
                   end * 100, 2) cr,
                   round(case when kpf.leads isnull then 0 else kpf.leads end /
                   case
                       when cab.clicks = 0 then 1
                       else cab.clicks
                   end * 100, 2) kpf_cr,
                   round(cab.cost_ /
                   case
                       when lead.leads = 0 then 1
                       else lead.leads
                   end, 2) cpl,
                   round(cab.cost_ /
                   case
                       when kpf.leads = 0 or kpf.leads isnull then 1
                       else kpf.leads
                   end, 2) kpf_cpl
            
            from
            (select
                   agency_client_id,
                   source,
                   sum(cost_) cost_,
                   sum(impressions) impressions,
                   sum(clicks) clicks
            from cabinets
            where source in ('vk_di', 'mytarget_di') and date between '{start_date}' and '{end_date}' and
            channel != 'smm'
            group by source, agency_client_id
            ) cab left join
            (
                select
                    agency_client_id,
                    count(*) leads,
                    utm_source
                from amo_kpf
                where lead_type = 'kpf' and date between '{start_date}' and '{end_date}' and channel != 'smm'
                group by agency_client_id, utm_source
            ) kpf on kpf.utm_source = cab.source and kpf.agency_client_id = cab.agency_client_id
            left join
            (
                select
                    agency_client_id,
                    count(*) leads,
                    utm_source
                from amo_kpf
                where lead_type = 'leads' and date between '{start_date}' and '{end_date}' and channel != 'smm'
                group by agency_client_id, utm_source
            ) lead on lead.utm_source = cab.source and lead.agency_client_id = cab.agency_client_id
            where cab.agency_client_id={agency_client_id}
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_smm_nvm(self, agency_client_id: int, start_date: str, end_date: str):
        cursor = connection.cursor()
        sql = f"""
            select
                    cab.agency_client_id agency_client_id,
                    cab.source source,
                    cab.cost_ cost_,
                    cab.impressions impressions,
                    cab.clicks clicks,
                   round(cab.clicks /
                   case
                       when cab.impressions = 0 then 1
                       else cab.impressions
                   end * 100, 2) ctr,
                   round(cab.cost_ /
                   case
                       when cab.clicks = 0 then 1
                       else cab.clicks
                   end, 2) cpc
            from
            (select
                   agency_client_id,
                   source,
                   sum(cost_) cost_,
                   sum(impressions) impressions,
                   sum(clicks) clicks
            from cabinets
            where source in ('vk_di', 'mytarget_di') and
                  date between '{start_date}' and '{end_date}' and
                  channel = 'smm'
            group by source, agency_client_id
            ) cab 
            where cab.agency_client_id={agency_client_id}
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report


class Reports(AgencyClients):
    objects = ReportsQuerySet.as_manager()

    class Meta:
        proxy = True
