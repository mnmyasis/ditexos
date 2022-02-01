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

    def get_brand_nvm(self, *args, **kwargs):
        agency_client_id = kwargs.get('agency_client_id')
        is_brand = kwargs.get('is_brand')
        direction_name = kwargs.get('direction_name')
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        is_main = kwargs.get('is_main')
        if is_main:  # Признак направлния "Общее"
            directions = kwargs.get('directions')
            if len(directions) == 1:  # Если нет необходимости выделять направление
                filter_campaign = "campaign ~* ''"
                filter_utm_campaign = "utm_campaign ~* ''"
            else:  # Исключение выделенных направлений из общей статистики
                filter_campaign = " and ".join(
                    [f"campaign !~* '{line.direction}'" for line in directions if line.is_main is False]
                )
                filter_utm_campaign = " and ".join(
                    [f"utm_campaign !~* '{line.direction}'" for line in directions if line.is_main is False]
                )
        else:  # Выделение статистики по направлению
            filter_utm_campaign = f"utm_campaign ~* '{direction_name}'"
            filter_campaign = f"campaign ~* '{direction_name}'"
        cursor = connection.cursor()
        sql = f"""
            select amo_report.agency_client_id,
                   amo_report.source,
                   amo_report.channel,
                   amo_report.source_ || amo_report.channel_ t_source,
                   round(amo_report.cost_, 2) cost_,
                   amo_report.clicks,
                   amo_report.impressions,
                   amo_report.leads,
                   amo_report.kpf,
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
                   round(amo_report.cost_ /
                   case
                       when amo_report.leads = 0 then 1
                       else amo_report.leads
                   end, 2) cpl,
                   round(amo_report.cost_ /
                   case
                       when amo_report.kpf = 0 then 1
                       else amo_report.kpf
                   end, 2) kpf_cpl
            from (
                select cab.agency_client_id,
                       cab.source,
                       cab.channel,
                       case
                           when cab.source = 'google' THEN 'Google Ads'
                           when cab.source = 'yandex' THEN 'Яндекс Директ'
                       END source_,
                       case
                           when cab.channel ~* 'master' THEN ' - Мастер'
                           when cab.channel ~* 'search' THEN ' - Поиск'
                           when cab.channel ~* 'network' and cab.source = 'google' THEN ' - КМС'
                           when cab.channel ~* 'network' THEN ' - РСЯ'
                           when cab.channel ~* 'discovery' THEN ' - Discovery'
                           when cab.channel ~* 'performance_max' THEN ' - Performance_max'
                           when cab.channel isnull and cab.source = 'yandex' THEN ' - Поиск'
                       END channel_,
                       cab.cost_,
                       cab.clicks,
                       cab.impressions impressions,
                       case when kpf.leads is NULL then 0
                           else kpf.leads
                       end kpf,
                       case when lead.leads is NULL then 0
                           else lead.leads
                       end leads
                from (
                    select
                       agency_client_id,
                       source,
                       channel,
                       is_brand,
                       sum(cost_) cost_,
                       sum(clicks) clicks,
                       sum(impressions) impressions
                    from cabinets
                    where is_brand={is_brand} and
                    date between '{start_date}' and '{end_date}'
                    and {filter_campaign}
                    and agency_client_id={agency_client_id}
                    group by agency_client_id, source, channel, is_brand
                ) cab
                left join (
                    select
                           agency_client_id,
                           count(*) leads,
                           utm_source,
                           case
                               when utm_campaign isnull THEN 'search'
                               when utm_campaign ~* '_master' THEN 'master'
                               when utm_campaign ~* 'master_kviz_krd' THEN 'master'
                               when utm_campaign ~* '_search' THEN 'search'
                               when utm_campaign ~* 'kazakhstan_kviz_mkb' THEN 'search'
                               when utm_campaign ~* 'discovery_' and utm_source = 'google' THEN 'discovery'
                               when utm_campaign ~* '_network' THEN 'network'
                               when utm_campaign ~* 'performance_max' and utm_source = 'google' THEN 'performance_max'
                               when utm_campaign ~* 'perfomance_max' and utm_source = 'google' THEN 'performance_max'
                           END channel,
                           case
                               when utm_campaign ~* '_brand' THEN True
                               when utm_campaign ~* 'brand_' THEN True
                               when utm_campaign ~* '_brand_' THEN True
                           else False
                           END is_brand
                    from amo_kpf where lead_type='kpf' and utm_source in ('google', 'yandex')
                    and {filter_utm_campaign}
                    and date between '{start_date}' and '{end_date}'
                    and agency_client_id={agency_client_id}
                    group by agency_client_id, utm_source, channel, is_brand
                    ) kpf on cab.source = kpf.utm_source and
                             cab.channel = kpf.channel and
                             cab.agency_client_id = kpf.agency_client_id and
                             cab.is_brand = kpf.is_brand
                    left join (
                        select
                           agency_client_id,
                           count(*) leads,
                           utm_source,
                           case
                               when utm_campaign isnull THEN 'search'
                               when utm_campaign ~* '_master' THEN 'master'
                               when utm_campaign ~* 'master_kviz_krd' THEN 'master'
                               when utm_campaign ~* '_search' THEN 'search'
                               when utm_campaign ~* 'kazakhstan_kviz_mkb' THEN 'search'
                               when utm_campaign ~* 'discovery_' and utm_source = 'google' THEN 'discovery'
                               when utm_campaign ~* '_network' THEN 'network'
                               when utm_campaign ~* 'performance_max' and utm_source = 'google' THEN 'performance_max'
                               when utm_campaign ~* 'perfomance_max' and utm_source = 'google' THEN 'performance_max'
                           END channel,
                           case
                               when utm_campaign ~* '_brand' THEN True
                               when utm_campaign ~* 'brand_' THEN True
                               when utm_campaign ~* '_brand_' THEN True
                           else False
                           END is_brand
                    from amo_kpf where lead_type='leads' and utm_source in ('google', 'yandex')
                        and {filter_utm_campaign}
                        and date between '{start_date}' and '{end_date}'
                        and agency_client_id={agency_client_id}
                    group by agency_client_id, utm_source, channel, is_brand
                    ) lead on cab.source = lead.utm_source and
                              cab.channel = lead.channel and
                              cab.agency_client_id = lead.agency_client_id and
                              cab.is_brand = lead.is_brand
              where cab.channel is not null
            ) amo_report;
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_week_nvm(self, agency_client_id):
        cursor = connection.cursor()
        sql = f"""
        select amo_report.agency_client_id,
               amo_report.week,
                amo_report.channel_,
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
                   cab.source_ || cab.channel_ channel_,
                   cab.week,
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
                   channel,
                   source,
                   case
                       when source = 'google' THEN 'Google Ads'
                       when source = 'yandex' THEN 'Яндекс Директ'
                   END source_,
                   case
                       when channel ~* 'master' THEN ' - Мастер'
                       when channel ~* 'search' THEN ' - Поиск'
                       when channel ~* 'network' and source = 'google' THEN ' - КМС'
                       when channel ~* 'network' THEN ' - РСЯ'
                       when channel ~* 'discovery' THEN ' - Discovery'
                       when channel ~* 'performance_max' THEN ' - Performance_max'
                       when channel isnull and source= 'yandex' THEN ' - Поиск'
                   END channel_,
                   sum(cost_) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   date_trunc('week', date)::date || ' - ' || (date_trunc('week', date) + '6 day'::interval)::date week,
                   date as date
                from cabinets
                group by agency_client_id, source, channel, date, week
            ) cab
            left join (
                select
                       count(*) leads,
                       agency_client_id,
                       utm_source,
                       case
                           when utm_campaign isnull THEN 'search'
                           when utm_campaign ~* '_master' THEN 'master'
                           when utm_campaign ~* 'master_kviz_krd' THEN 'master'
                           when utm_campaign ~* '_search' THEN 'search'
                           when utm_campaign ~* 'kazakhstan_kviz_mkb' THEN 'search'
                           when utm_campaign ~* '_search' THEN 'search'
                           when utm_campaign ~* 'discovery_' and utm_source = 'google' THEN 'discovery'
                           when utm_campaign ~* '_network' THEN 'network'
                           when utm_campaign ~* 'performance_max' and utm_source = 'google' THEN 'performance_max'
                           when utm_campaign ~* 'perfomance_max' and utm_source = 'google' THEN 'performance_max'
                       END amo_channel,
                       date
                from amo_kpf where lead_type='gk'
                and utm_source in ('google', 'yandex')
                group by agency_client_id, utm_source, amo_channel, date
                ) gk on cab.agency_client_id = gk.agency_client_id and
                        cab.source = gk.utm_source and
                        cab.date = gk.date and
                        cab.channel = gk.amo_channel
                left join (
                    select
                       count(*) leads,
                       agency_client_id,
                       utm_source,
                       case
                           when utm_campaign isnull THEN 'search'
                           when utm_campaign ~* '_master' THEN 'master'
                           when utm_campaign ~* 'master_kviz_krd' THEN 'master'
                           when utm_campaign ~* '_search' THEN 'search'
                           when utm_campaign ~* 'kazakhstan_kviz_mkb' THEN 'search'
                           when utm_campaign ~* 'discovery_' and utm_source = 'google' THEN 'discovery'
                           when utm_campaign ~* '_network' THEN 'network'
                           when utm_campaign ~* 'performance_max' and utm_source = 'google' THEN 'performance_max'
                           when utm_campaign ~* 'perfomance_max' and utm_source = 'google' THEN 'performance_max'
                       END amo_channel,
                       date
                from amo_kpf where lead_type='leads'
                               and utm_source in ('google', 'yandex')
                group by agency_client_id, utm_source, amo_channel, date
                ) lead on cab.agency_client_id = lead.agency_client_id and
                          cab.source = lead.utm_source and
                          cab.channel = lead.amo_channel and
                          cab.date = lead.date
            where cab.agency_client_id = {agency_client_id} and cab.week is not null
            group by cab.agency_client_id, cab.week, cab.source, cab.source_, cab.channel_
        ) amo_report order by week DESC;
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
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report


class Reports(AgencyClients):
    objects = ReportsQuerySet.as_manager()

    class Meta:
        proxy = True
