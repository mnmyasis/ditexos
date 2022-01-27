create view cabinet_for_comagic_campaign_report
as
select
       cab_report.agency_client_id,
       cab_report.source,
       cab_report.campaign,
       cab_report.campaign_id,
       cab_report.channel,
       cab_report.direction,
       cab_report.cost_,
       cab_report.clicks,
       cab_report.impressions,
       cab_report.call_leads,
       cab_report.chat_leads,
       cab_report.site_leads,
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
       round((cab_report.call_leads + cab_report.chat_leads + cab_report.site_leads) /
       case
           when cab_report.clicks = 0 then 1
           else cab_report.clicks
       end * 100, 2) cr,
       round(cab_report.cost_ /
       case
           when (cab_report.call_leads + cab_report.chat_leads + cab_report.site_leads) = 0 then 1
           else (cab_report.call_leads + cab_report.chat_leads + cab_report.site_leads)
       end, 2) cpl,
       cab_report.date
from (
    select
           cabinet.id agency_client_id,
           cabinet.source,
           cabinet.campaign,
           cabinet.campaign_id,
           case
               when campaign ~* '_search' THEN 'search'
               when campaign ~* '_network' THEN 'network'
           END channel,
           case
               when campaign ~* '_search' THEN replace(campaign, '_search', '')
               when campaign ~* '_network' THEN replace(campaign, '_network', '')
           END direction,
           case when cabinet.cost_ is NULL then 0
               else cabinet.cost_
           end cost_,
           case when cabinet.clicks is Null then 0
                else cabinet.clicks
           end clicks,
           case when cabinet.impressions is NULL then 0
                else cabinet.impressions
           end impressions,
           case
               when call.leads is NULL then 0
               else call.leads
           end call_leads,
           case when chat.leads is NULL then 0
               else chat.leads
           end chat_leads,
           case when site.leads is Null then 0
               else site.leads
           end site_leads,
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
    ) cabinet
    left join (
        select co_api.id,
               co_api.agency_client_id,
               cr.utm_source,
               cr.utm_campaign,
               count(cr.utm_campaign) leads,
               cr.date
        from comagic_api_token co_api
        left join comagic_report cr on co_api.id = cr.api_client_id
        where (cr.utm_source = 'yandex' or cr.utm_source = 'google') and
              cr.source_type = 'call'
        group by co_api.id, co_api.agency_client_id, cr.utm_source, cr.utm_campaign, cr.date
        ) call on cabinet.id = call.agency_client_id and
                  cabinet.source = call.utm_source and
                  cabinet.date = call.date and
                  cabinet.campaign = call.utm_campaign
    left join (
        select co_api.id,
               co_api.agency_client_id,
               cr.utm_source,
               cr.utm_campaign,
               count(cr.utm_campaign) leads,
               cr.date
        from comagic_api_token co_api
        left join comagic_report cr on co_api.id = cr.api_client_id
        where (cr.utm_source = 'yandex' or cr.utm_source = 'google') and
              cr.source_type = 'chat'
        group by co_api.id, co_api.agency_client_id, cr.utm_source, cr.utm_campaign, cr.date
        ) chat on cabinet.id = chat.agency_client_id and
                  cabinet.source = chat.utm_source and
                  cabinet.date = chat.date and
                  cabinet.campaign = chat.utm_campaign
    left join (
        select co_api.id,
               co_api.agency_client_id,
               cr.utm_source,
               cr.utm_campaign,
               count(cr.utm_campaign) leads,
               cr.date
        from comagic_api_token co_api
        left join comagic_report cr on co_api.id = cr.api_client_id
        where (cr.utm_source = 'yandex' or cr.utm_source = 'google') and
              cr.source_type = 'site'
        group by co_api.id, co_api.agency_client_id, cr.utm_source, cr.utm_campaign, cr.date
        ) site on cabinet.id = site.agency_client_id and
                  cabinet.source = site.utm_source and
                  cabinet.date = site.date and
                  cabinet.campaign = site.utm_campaign
) cab_report;