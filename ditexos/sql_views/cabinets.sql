create view cabinets
as
select cab_report.agency_client_id,
       cab_report.source,
       cab_report.campaign,
       cab_report.campaign_id,
       cab_report.channel,
       case
           when cab_report.source = 'google' THEN 'Google Ads'
           when cab_report.source = 'yandex' THEN 'Яндекс Директ'
           when cab_report.source = 'vk_di' THEN 'Вконтакте'
           when cab_report.source = 'mytarget_di' THEN 'MyTarget'
           END                                                         source_name,
       case
           when cab_report.channel = 'smm' THEN ' - SMM'
           when cab_report.channel = 'vk_target' THEN ' - LEADGEN'
           when cab_report.channel = 'my_target' THEN ' - LEADGEN'
           when cab_report.channel = 'mkb' THEN ' - МКБ'
           when cab_report.channel = 'master' THEN ' - Мастер'
           when cab_report.channel = 'search' THEN ' - Поиск'
           when cab_report.channel = 'network' and source = 'google' THEN ' - КМС'
           when cab_report.channel = 'network' THEN ' - РСЯ'
           when cab_report.channel = 'discovery' THEN ' - Discovery'
           when cab_report.channel = 'video' THEN ' - Video'
           when cab_report.channel = 'performance_max' THEN ' - Performance_max'
           when cab_report.channel isnull and source = 'yandex' THEN ' - Поиск'
           END                                                         channel_name,
       cab_report.direction,
       cab_report.is_brand,
       cab_report.cost_,
       cab_report.clicks,
       cab_report.impressions,
       cab_report.date,
       date_trunc('week', cab_report.date)::date || ' - ' ||
       (date_trunc('week', cab_report.date) + '6 day'::interval)::date week,
       date_trunc('month', cab_report.date)                            month_,
       to_char(date_trunc('month', cab_report.date), 'YYYY - MONTH')   month_string
from (
         select cabinet.id agency_client_id,
                cabinet.source,
                cabinet.campaign,
                cabinet.campaign_id,
                case
                    when campaign isnull and source = 'yandex' THEN 'cutaway'
                    when campaign ~* 'mkb' THEN 'mkb'
                    when campaign ~* 'master' THEN 'master'
                    when campaign ~* 'general_kviz_krd' THEN 'search'
                    when campaign ~* 'master_kviz_krd' THEN 'master'
                    when campaign ~* 'kazakhstan_kviz_mkb' THEN 'search'
                    when campaign ~* 'search' THEN 'search'
                    when campaign ~* 'discovery' and source = 'google' THEN 'discovery'
                    when campaign ~* 'network' THEN 'network'
                    when campaign ~* 'video' and source = 'google' THEN 'video'
                    when campaign ~* 'performance_max' and source = 'google' THEN 'performance_max'
                    when campaign ~* 'perfomance_max' and source = 'google' THEN 'performance_max'
                    when campaign ~* 'smm' and source in ('vk_di', 'mytarget_di') THEN 'smm'
                    when campaign !~* 'smm' and source = 'vk_di' THEN 'vk_target'
                    when campaign !~* 'smm' and source = 'mytarget_di' THEN 'my_target'
                    END    channel,
                case
                    when campaign ~* '_search' THEN replace(campaign, '_search', '')
                    when campaign ~* '_network' THEN replace(campaign, '_network', '')
                    END    direction,
                case
                    when campaign ~* '_brand' THEN True
                    when campaign ~* 'brand_' THEN True
                    when campaign ~* '_brand_' THEN True
                    else False
                    END    is_brand,
                case
                    when cabinet.cost_ is NULL then 0
                    else cabinet.cost_
                    end    cost_,
                case
                    when cabinet.clicks is Null then 0
                    else cabinet.clicks
                    end    clicks,
                case
                    when cabinet.impressions is NULL then 0
                    else cabinet.impressions
                    end    impressions,
                cabinet.date
         from (
                  select id,
                         'yandex'         source,
                         campaign,
                         campaign_id,
                         sum(cost_)       cost_,
                         sum(clicks)      clicks,
                         sum(impressions) impressions,
                         date
                  from yandex_report_view
                  group by id, campaign, campaign_id, date
                  union all
                  (select id,
                          'google'         source,
                          campaign,
                          campaign_id,
                          sum(cost_)       cost_,
                          sum(clicks)      clicks,
                          sum(impressions) impressions,
                          date
                   from google_report_view
                   group by id, campaign, campaign_id, date
                  )
                  union all
                  (select id,
                          'vk_di'          source,
                          campaign,
                          campaign_id,
                          sum(cost_)       cost_,
                          sum(clicks)      clicks,
                          sum(impressions) impressions,
                          date
                   from vk_report_view
                   group by id, campaign, campaign_id, date
                  )
                  union all
                  (
                      select id,
                             'mytarget_di'               source,
                             campaign,
                             campaign_id,
                             cast(sum(cost_) as numeric) cost_,
                             sum(clicks)                 clicks,
                             sum(impressions)            impressions,
                             date
                      from my_target_view
                      group by id, campaign, campaign_id, date
                  )
              ) cabinet
         where cabinet.date is not null
     ) cab_report;
