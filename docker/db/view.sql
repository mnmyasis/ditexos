create view yandex_report_view
as
select
    agc_cl.id id,
    agc_cl.name agency_client_name,
    agc_cl.call_tracker_object_id call_tracker_id,
    yandex.id yandex_client_id,
    yandex.campaign campaign,
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
        group by ya_cl.id, yc.name, ykw.name, ym.date
    ) as yandex on agc_cl.yandex_client_id = yandex.id;

create view google_report_view
as
select
       agc_cl.id id,
       agc_cl.name agency_client_name,
       google.google_client_id google_client_id,
       google.campaign campaign,
       google.key_word key_word,
       google.cost cost_,
       google.clicks clicks,
       google.impressions impressions,
       google.date date
from agency_clients agc_cl
left join (
    select
           gog_cl.id google_client_id,
           gc.name campaign,
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
    group by gog_cl.id, gm.date, gc.name, gkw.name
) google on google.google_client_id = agc_cl.google_client_id;