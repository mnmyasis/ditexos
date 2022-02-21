create view cabinets
as
select
       cab_report.agency_client_id,
       cab_report.source,
       cab_report.campaign,
       cab_report.campaign_id,
       cab_report.channel,
       cab_report.direction,
       cab_report.is_brand,
       cab_report.cost_,
       cab_report.clicks,
       cab_report.impressions,
       round(cab_report.clicks /
       case
           when cab_report.impressions = 0 then 1
           else cab_report.impressions
       end * 100, 2) ctr,
       round(cab_report.cost_ /
       case
           when cab_report.clicks = 0 then 1
           else cab_report.clicks
       end, 2) cpc,
       cab_report.date
from (
    select
           cabinet.id agency_client_id,
           cabinet.source,
           cabinet.campaign,
           cabinet.campaign_id,
           case
               when campaign ~* 'smm' and source in ('vk_di', 'mytarget_di') THEN 'smm'
               when campaign !~* 'smm' and source = 'vk_di' THEN 'vk_target'
               when campaign !~* 'smm' and source = 'mytarget_di' THEN 'my_target'
               when campaign ~* '_mkb' THEN 'mkb'
               when campaign ~* '_master' THEN 'master'
               when campaign ~* 'master_kviz_krd' THEN 'master'
               when campaign ~* '_search' THEN 'search'
               when campaign ~* 'discovery' and source = 'google' THEN 'discovery'
               when campaign ~* '_network' THEN 'network'
               when campaign ~* 'performance_max' and source = 'google' THEN 'performance_max'
               when campaign ~* 'perfomance_max' and source = 'google' THEN 'performance_max'
           END channel,
           case
               when campaign ~* '_search' THEN replace(campaign, '_search', '')
               when campaign ~* '_network' THEN replace(campaign, '_network', '')
           END direction,
           case
               when campaign ~* '_brand' THEN True
               when campaign ~* 'brand_' THEN True
               when campaign ~* '_brand_' THEN True
               else False
           END is_brand,
           case when cabinet.cost_ is NULL then 0
               else cabinet.cost_
           end cost_,
           case when cabinet.clicks is Null then 0
                else cabinet.clicks
           end clicks,
           case when cabinet.impressions is NULL then 0
                else cabinet.impressions
           end impressions,
           cabinet.date
    from (
        select * from (
        select id,
            'yandex' source,
            campaign,
            campaign_id,
            sum(cost_) cost_,
            sum(clicks) clicks,
            sum(impressions) impressions,
            date
        from yandex_report_view
        group by id, campaign, campaign_id, date
        ) ads
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
        group by id, campaign, campaign_id, date
        )
        union all
        (
            select
                   id,
                   'mytarget_di' source,
                   campaign,
                   campaign_id,
                   cast(sum(cost_) as numeric) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   date
            from my_target_view
            group by id, campaign, campaign_id, date
        )
    ) cabinet
) cab_report;