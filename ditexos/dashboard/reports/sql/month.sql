select agency_client_id,
       source,
       month_ as                   month_string,
       source_name,
       sum(impressions)::int       impressions,
       round(sum(cost_), 2)::float cost_,
       sum(clicks)::int            clicks,
       month_,
       (
           select count(*)
           from amo_kpf
           where agency_client_id = {agency_client_id} and lead_type = 'leads' and cabinets.source = utm_source and cabinets.month_ = month_ ) leads,
    (
select count(*)
from amo_kpf
where agency_client_id = {agency_client_id}
  and lead_type = 'gk'
  and cabinets.source = utm_source
  and cabinets.month_ = month_
    ) gk
from cabinets
where agency_client_id = {agency_client_id}
group by agency_client_id, source, source_name, month_, month_string
order by month_ desc;
