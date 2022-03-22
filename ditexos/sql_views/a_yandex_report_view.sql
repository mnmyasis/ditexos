create view yandex_report_view
as
select
    agc_cl.id id,
    agc_cl.name agency_client_name,
    yandex.id yandex_client_id,
    yandex.campaign campaign,
    yandex.campaign_id campaign_id,
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
            round(cast(sum(ym.cost) as numeric), 2) as cost,
            sum(ym.clicks) clicks,
            sum(ym.impressions) impressions,
            ym.date date
            from yandex_clients ya_cl
            left join yandex_campaigns yc on ya_cl.id = yc.client_id
            left join yandex_metrics ym on ym.campaign_id = yc.id
        group by ya_cl.id, yc.name, yc.campaign_id, ym.date
    ) as yandex on agc_cl.yandex_client_id = yandex.id;