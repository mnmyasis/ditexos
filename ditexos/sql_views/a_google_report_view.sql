create view google_report_view
as
select
       agc_cl.id id,
       agc_cl.name agency_client_name,
       google.google_client_id google_client_id,
       google.campaign campaign,
       google.campaign_id campaign_id,
       google.key_word key_word,
       google.cost * 1.2 cost_,
       google.clicks clicks,
       google.impressions impressions,
       google.date date

from agency_clients agc_cl
left join (
    select
           gog_cl.id google_client_id,
           gc.name campaign,
           gc.campaign_id,
           gkw.name key_word,
           sum(gm.cost_micros * 0.000001) as cost,
           sum(gm.clicks) clicks,
           sum(gm.impressions) impressions,
           gm.date date
    from google_clients gog_cl
             left join google_campaigns gc on gog_cl.id = gc.client_id
             left join google_ad_groups gag on gc.id = gag.campaign_id
             left join google_key_words gkw on gag.id = gkw.ad_group_id
             left join google_metrics gm on gkw.id = gm.key_word_id or gc.id = gm.campaign_id
    group by gog_cl.id, gm.date, gc.name, gc.campaign_id, gkw.name
) google on google.google_client_id = agc_cl.google_client_id;