select amo_report.month_,
       amo_report.agency_client_id,
       amo_report.month_string,
       amo_report.source,
       amo_report.source_name,
       amo_report.campaign,
       round(amo_report.cost_, 2)::float cost_,
       amo_report.clicks::int,
       amo_report.impressions::int,
       amo_report.leads::int,
       amo_report.gk::int
from (
         select cab.agency_client_id,
                cab.source,
                cab.source_name,
                cab.campaign,
                cab.month_string,
                cab.month_,
                sum(cab.cost_)       cost_,
                sum(cab.clicks)      clicks,
                sum(cab.impressions) impressions,
                sum(case
                        when gk.leads is NULL then 0
                        else gk.leads
                    end)             gk,
                sum(case
                        when lead.leads is NULL then 0
                        else lead.leads
                    end)             leads
         from (
                  select agency_client_id,
                         source,
                         source_name,
                         campaign,
                         sum(cost_)       cost_,
                         sum(clicks)      clicks,
                         sum(impressions) impressions,
                         month_,
                         month_string
                  from cabinets
                  where agency_client_id ={agency_client_id} and date is not null
                  group by agency_client_id, source, source_name, campaign, month_, month_string
              ) cab

                  left join (
             select agency_client_id,
                    count(*) leads,
                    utm_source,
                    case
                        when utm_campaign ~* 'yuzhnaya_stolica_kviz_krd_search'
                            THEN 'yuzhnaya_stolica_kviz_krd_brand_search'
                        when utm_campaign ~* 'zolotoj_gorod_kviz_rf_search' THEN 'zolotoj_gorod_kviz_krd_brand_search'
                        when utm_campaign ~* 'perfomance_max' THEN 'performance_max'
                        when utm_campaign is null and utm_source = 'yandex' THEN 'yandex_cutaway'
                        when utm_campaign is null and utm_source = 'google' THEN 'google_cutaway'
                        else utm_campaign
                        END  utm_campaign,
                    month_
             from amo_kpf
             where lead_type = 'gk'
             group by agency_client_id, utm_source, utm_campaign, month_
         ) gk on cab.source = gk.utm_source and
                 cab.campaign = gk.utm_campaign and
                 cab.month_ = gk.month_ and
                 cab.agency_client_id = gk.agency_client_id
                  left join (
             select agency_client_id,
                    count(*) leads,
                    utm_source,
                    case
                        when utm_campaign ~* 'yuzhnaya_stolica_kviz_krd_search'
                            THEN 'yuzhnaya_stolica_kviz_krd_brand_search'
                        when utm_campaign ~* 'zolotoj_gorod_kviz_rf_search' THEN 'zolotoj_gorod_kviz_krd_brand_search'
                        when utm_campaign ~* 'perfomance_max' THEN 'performance_max'
                        when utm_campaign is null and utm_source = 'yandex' THEN 'yandex_cutaway'
                        when utm_campaign is null and utm_source = 'google' THEN 'google_cutaway'
                        else utm_campaign
                        END  utm_campaign,
                    month_
             from amo_kpf
             where lead_type = 'leads'
             group by agency_client_id, utm_source, utm_campaign, month_
         ) lead on cab.source = lead.utm_source and
                   cab.campaign = lead.utm_campaign and
                   cab.month_ = lead.month_ and
                   cab.agency_client_id = lead.agency_client_id
         where cab.agency_client_id = {agency_client_id}
         group by cab.agency_client_id, cab.source, cab.source_name, cab.campaign, cab.month_, cab.month_string
         union
         (
         select leads.agency_client_id,
             leads.source,
             source source_name,
             leads.campaign,
             month_string,
             month_,
             0 clicks,
             0 impressions,
             0 cost_,
             sum(case
             when leads.gk is null then 0
             else leads.gk
             end) gk,
             sum(case
             when leads.leads is null then 0
             else leads.leads
             end) leads
         from (select
             agency_client_id,
             utm_source as source,
             case
             when utm_campaign is null and utm_source = 'yandex' THEN 'yandex_cutaway'
             when utm_campaign is null and utm_source = 'google' THEN 'google_cutaway'
             else utm_campaign
             END campaign,
             case
             when lead_type = 'leads' THEN count(lead_type)
             end leads,
             case
             when lead_type = 'gk' THEN count(lead_type)
             end gk,
             month_,
             month_string
             from amo_kpf where
             utm_campaign is null and
             utm_source in ('google', 'yandex') and
             agency_client_id = {agency_client_id}
             group by agency_client_id, lead_type, utm_source, source, utm_campaign, campaign, month_, month_string) leads
         group by leads.agency_client_id, leads.source, source_name, leads.campaign, month_string, month_

             )
     ) amo_report
order by month_ DESC, source ASC;