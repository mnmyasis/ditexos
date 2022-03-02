create view vk_report_view
as
select agency_clients.id id,
       agency_clients.name agency_client_name,
       vk_cab.id vk_client_id,
       vk_cab.campaign campaign,
       vk_cab.campaign_id campaign_id,
       vk_cab.cost cost_,
       vk_cab.clicks clicks,
       vk_cab.impressions impressions,
       vk_cab.date date
from agency_clients left join
(select vk_clients.id,
        vk_campaigns.name campaign,
        vk_campaigns.campaign_id,
        round(cast(sum(vk_metrics.spent) as numeric), 2) as cost,
        sum(vk_metrics.clicks) clicks,
        sum(vk_metrics.impressions) impressions,
        vk_metrics.date
from vk_token
    left join vk_ads_accounts on vk_token.id = vk_ads_accounts.token_vk_id
    left join vk_clients on vk_ads_accounts.id = vk_clients.account_id
    left join vk_campaigns on vk_clients.id = vk_campaigns.client_id
    left join vk_metrics on vk_campaigns.id = vk_metrics.campaign_id
group by vk_clients.id, vk_campaigns.name, vk_campaigns.campaign_id, vk_metrics.date
    ) vk_cab on agency_clients.vk_client_id = vk_cab.id;