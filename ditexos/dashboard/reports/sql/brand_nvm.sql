SELECT br.agency_client_id,
       br.channel ch,
       br.source_name || br.channel_name channel,
       ROUND(br.cost_, 2)                cost_,
       br.impressions,
       br.clicks,
       br.leads,
       br.kpf
FROM(
     SELECT agency_client_id,
            source,
            source_name,
            channel,
            channel_name,
            SUM(cost_)       cost_,
            SUM(impressions) impressions,
            SUM(clicks)      clicks,
    (SELECT COUNT(*)
     FROM amo_kpf
     WHERE agency_client_id = {agency_client_id}
         AND date BETWEEN '{start_date}'
         AND '{end_date}'
         AND lead_type = 'leads'
         AND {filter_utm_campaign}
         AND is_brand = {is_brand}
         AND cabinets.source = utm_source
         AND cabinets.channel = channel) leads,
     (SELECT COUNT(*)
      FROM amo_kpf
      WHERE agency_client_id = {agency_client_id}
        AND date BETWEEN '{start_date}'
        AND '{end_date}'
        AND lead_type = 'kpf'
        AND {filter_utm_campaign}
        AND is_brand = {is_brand}
        AND cabinets.source = utm_source
        AND cabinets.channel = channel) kpf
    FROM cabinets
WHERE agency_client_id = {agency_client_id}
  AND date BETWEEN '{start_date}'
  AND '{end_date}'
  AND source IN ('yandex', 'google')
  AND is_brand = {is_brand}
  AND {filter_campaign}
GROUP BY agency_client_id, source, source_name, channel, channel_name) br;