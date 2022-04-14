SELECT agency_client_id,
       source,
       source_name,
       week,
       channel_name,
       source_name || channel_name      channel,
       channel                          ch,
       sum(impressions)::int            impressions,
       round(sum(cost_), 2) ::float     cost_,
       sum(clicks)::int                 clicks,
       (SELECT count(*) leads
        FROM amo_kpf
        WHERE agency_client_id = {agency_client_id}
    AND week = cabinets.week
    AND lead_type = 'leads'
    AND channel = cabinets.channel
    AND utm_source = cabinets.source) leads,
    (
SELECT count(*) leads
FROM amo_kpf
WHERE agency_client_id = {agency_client_id}
  AND week = cabinets.week
  AND lead_type = 'gk'
  AND channel = cabinets.channel
  AND utm_source = cabinets.source) gk
FROM cabinets
WHERE agency_client_id = {agency_client_id}
GROUP BY agency_client_id, source, source_name, ch, channel_name, week
ORDER BY week DESC, channel;