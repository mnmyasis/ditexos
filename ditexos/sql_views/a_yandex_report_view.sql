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