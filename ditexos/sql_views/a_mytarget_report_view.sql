create view my_target_view
as
select
       agency_clients.id id,
       agency_clients.name agency_client_name,
       mtc.id my_target_client_id,
       m.name campaign,
       m.campaign_id campaign_id,
       mtm.spent cost_,
       mtm.clicks clicks,
       mtm.impressions impressions,
       mtm.date date
from agency_clients left join
    my_target_clients mtc on mtc.id = agency_clients.my_target_client_id left join
    my_target_campaigns m on mtc.id = m.client_id left join
    my_target_metrics mtm on m.id = mtm.campaign_id;