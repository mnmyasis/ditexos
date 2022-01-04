create view yandex_report_view
as
select
    agc_cl.id id,
    agc_cl.name agency_client_name,
    yandex.id yandex_client_id,
    yandex.campaign campaign,
    yandex.campaign_id campaign_id,
    yandex.key_word key_word,
    yandex.cost cost_,
    yandex.clicks clicks,
    yandex.impressions impressions,
    yandex.date date
from agency_clients agc_cl
left join (
     select
            ya_cl.id id,
            yc.name campaign,
            yc.campaign_id,
            ykw.name key_word,
            round(cast(sum(ym.cost) as numeric), 2) as cost,
            sum(ym.clicks) clicks,
            sum(ym.impressions) impressions,
            ym.date date
            from yandex_clients ya_cl
            left join yandex_campaigns yc on ya_cl.id = yc.client_id
            left join yandex_ad_groups yag on yc.id = yag.campaign_id
            left join yandex_key_words ykw on yag.id = ykw.ad_group_id
            left join yandex_metrics ym on ykw.id = ym.key_word_id
        group by ya_cl.id, yc.name, yc.campaign_id, ykw.name, ym.date
    ) as yandex on agc_cl.yandex_client_id = yandex.id;
create view google_report_view
as
select
       agc_cl.id id,
       agc_cl.name agency_client_name,
       google.google_client_id google_client_id,
       google.campaign campaign,
       google.campaign_id campaign_id,
       google.key_word key_word,
       google.cost * 1.2 cost_,
       google.clicks clicks,
       google.impressions impressions,
       google.date date

from agency_clients agc_cl
left join (
    select
           gog_cl.id google_client_id,
           gc.name campaign,
           gc.campaign_id,
           gkw.name key_word,
           sum(gm.cost_micros * 0.000001) as cost,
           sum(gm.clicks) clicks,
           sum(gm.impressions) impressions,
           gm.date date
    from google_clients gog_cl
             left join google_campaigns gc on gog_cl.id = gc.client_id
             left join google_ad_groups gag on gc.id = gag.campaign_id
             left join google_key_words gkw on gag.id = gkw.ad_group_id
             left join google_metrics gm on gkw.id = gm.key_word_id
    group by gog_cl.id, gm.date, gc.name, gc.campaign_id, gkw.name
) google on google.google_client_id = agc_cl.google_client_id;
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
create view cabinet_for_comagic_keyword_report
as
select
       cab_report.agency_client_id,
       cab_report.source,
       cab_report.campaign,
       cab_report.campaign_id,
       cab_report.key_word,
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
           cabinet.key_word,
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
            key_word,
            sum(cost_) cost_,
            sum(clicks) clicks,
            sum(impressions) impressions,
            date
        from yandex_report_view
        group by id, campaign, campaign_id, key_word, date
        ) ads
        union all
        (select id,
            'google' source,
            campaign,
            campaign_id,
            key_word,
            sum(cost_) cost_,
            sum(clicks) clicks,
            sum(impressions) impressions,
            date
        from google_report_view
        group by id, campaign, campaign_id, key_word, date
        )
    ) cabinet
    left join (
        select co_api.id,
               co_api.agency_client_id,
               cr.utm_source,
               cr.utm_campaign,
               cr.utm_term,
               count(cr.utm_campaign) leads,
               cr.date
        from comagic_api_token co_api
        left join comagic_report cr on co_api.id = cr.api_client_id
        where (cr.utm_source = 'yandex' or cr.utm_source = 'google') and
              cr.source_type = 'call'
        group by co_api.id, co_api.agency_client_id, cr.utm_source, cr.utm_campaign, cr.utm_term, cr.date
        ) call on cabinet.id = call.agency_client_id and
                  cabinet.source = call.utm_source and
                  cabinet.date = call.date and
                  cabinet.campaign = call.utm_campaign and
                  cabinet.key_word = call.utm_term
    left join (
        select co_api.id,
               co_api.agency_client_id,
               cr.utm_source,
               cr.utm_campaign,
               cr.utm_term,
               count(cr.utm_campaign) leads,
               cr.date
        from comagic_api_token co_api
        left join comagic_report cr on co_api.id = cr.api_client_id
        where (cr.utm_source = 'yandex' or cr.utm_source = 'google') and
              cr.source_type = 'chat'
        group by co_api.id, co_api.agency_client_id, cr.utm_source, cr.utm_campaign, cr.utm_term, cr.date
        ) chat on cabinet.id = chat.agency_client_id and
                  cabinet.source = chat.utm_source and
                  cabinet.date = chat.date and
                  cabinet.campaign = chat.utm_campaign and
                  cabinet.key_word = chat.utm_term
    left join (
        select co_api.id,
               co_api.agency_client_id,
               cr.utm_source,
               cr.utm_campaign,
               cr.utm_term,
               count(cr.utm_campaign) leads,
               cr.date
        from comagic_api_token co_api
        left join comagic_report cr on co_api.id = cr.api_client_id
        where (cr.utm_source = 'yandex' or cr.utm_source = 'google') and
              cr.source_type = 'site'
        group by co_api.id, co_api.agency_client_id, cr.utm_source, cr.utm_campaign, cr.utm_term, cr.date
        ) site on cabinet.id = site.agency_client_id and
                  cabinet.source = site.utm_source and
                  cabinet.date = site.date and
                  cabinet.campaign = site.utm_campaign and
                  cabinet.key_word = site.utm_term
) cab_report;

create view cabinets
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
) cab_report;