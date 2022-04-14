SELECT agency_client_id,
       source                      src,
       month_                      month_string,
       source_name                 source,
       SUM(impressions)::int       impressions,
       ROUND(SUM(cost_), 2)::float cost_,
       SUM(clicks)::int            clicks,
       month_,
       (
           SELECT COUNT(*)
           FROM amo_kpf
           WHERE agency_client_id = {agency_client_id}
           AND lead_type = 'leads'
           AND cabinets.source = utm_source
           AND cabinets.month_ = month_ ) leads,
    (
SELECT count(*)
FROM amo_kpf
WHERE agency_client_id = {agency_client_id}
  AND lead_type = 'gk'
  AND cabinets.source = utm_source
  AND cabinets.month_ = month_
    ) gk
FROM cabinets
WHERE agency_client_id = {agency_client_id}
GROUP BY agency_client_id, source, source_name, month_, month_string
ORDER BY month_ DESC;
