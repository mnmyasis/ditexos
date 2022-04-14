select cab.agency_client_id    agency_client_id,
       cab.source              source,
       cab.cost_               cost_,
       cab.impressions         impressions,
       cab.clicks              clicks
from (select agency_client_id,
             source,
             sum(cost_)       cost_,
             sum(impressions) impressions,
             sum(clicks)      clicks
      from cabinets
      where source in ('vk_di', 'mytarget_di')
        and date between '{start_date}' and '{end_date}'
        and channel = 'smm'
      group by source, agency_client_id
     ) cab
where cab.agency_client_id ={agency_client_id}