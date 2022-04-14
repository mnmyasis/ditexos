select cab.agency_client_id    agency_client_id,
       cab.source              source,
       cab.cost_               cost_,
       cab.impressions         impressions,
       cab.clicks              clicks,
       case
           when kpf.leads isnull Then 0
           else kpf.leads
           end                 kpf,
       case
           when lead.leads isnull Then 0
           else lead.leads
           end                 leads
from (select agency_client_id,
             source,
             sum(cost_)       cost_,
             sum(impressions) impressions,
             sum(clicks)      clicks
      from cabinets
      where source in ('vk_di', 'mytarget_di')
        and date between '{start_date}' and '{end_date}'
        and channel != 'smm'
      group by source, agency_client_id
     ) cab
         left join
     (
         select agency_client_id,
                count(*) leads,
                utm_source
         from amo_kpf
         where lead_type = 'kpf'
           and date between '{start_date}' and '{end_date}'
           and channel != 'smm'
         group by agency_client_id, utm_source
     ) kpf on kpf.utm_source = cab.source and kpf.agency_client_id = cab.agency_client_id
         left join
     (
         select agency_client_id,
                count(*) leads,
                utm_source
         from amo_kpf
         where lead_type = 'leads'
           and date between '{start_date}' and '{end_date}'
           and channel != 'smm'
         group by agency_client_id, utm_source
     ) lead on lead.utm_source = cab.source and lead.agency_client_id = cab.agency_client_id
where cab.agency_client_id ={agency_client_id}