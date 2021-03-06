create view amo_kpf
as
select amo.id,
       amo_and_agency.agencyclients_id                                  agency_client_id,
       'kpf'                                                            lead_type,
       metric.utm_source,
       metric.utm_campaign,
       metric.closed_at                                                 date,
       date_trunc('week', metric.closed_at)::date || ' - ' ||
       (date_trunc('week', metric.closed_at) + '6 day'::interval)::date week,
       date_trunc('month', metric.closed_at)                            month_,
       to_char(date_trunc('month', metric.closed_at), 'YYYY - MONTH')   month_string,
       case
           when metric.utm_campaign ~* 'smm' and metric.utm_source = 'vk_di' THEN 'smm'
           when metric.utm_source = 'vk_di' THEN 'vk_target'
           when metric.utm_campaign ~* 'smm' and utm_source = 'mytarget_di' THEN 'smm'
           when metric.utm_source = 'mytarget_di' THEN 'my_target'
           when metric.utm_campaign ~* 'mkb' THEN 'mkb'
           when metric.utm_campaign ~* 'video' THEN 'video'
           when metric.utm_campaign isnull THEN 'search'
           when metric.utm_campaign ~* 'master' THEN 'master'
           when metric.utm_campaign = 'general_kviz_krd' THEN 'search'
           when metric.utm_campaign ~* 'master_kviz_krd' THEN 'master'
           when metric.utm_campaign ~* 'search' THEN 'search'
           when metric.utm_campaign ~* 'discovery' and utm_source = 'google' THEN 'discovery'
           when metric.utm_campaign ~* 'network' THEN 'network'
           when metric.utm_campaign ~* 'performance_max' and utm_source = 'google' THEN 'performance_max'
           when metric.utm_campaign ~* 'perfomance_max' and utm_source = 'google' THEN 'performance_max'
           END                                                          channel,
       case
           when metric.utm_campaign ~* '_brand' THEN True
           when metric.utm_campaign ~* 'brand_' THEN True
           when metric.utm_campaign ~* '_brand_' THEN True
           else False
           END                                                          is_brand
from amo_crm amo
         left join amo_crm_and_agency_client amo_and_agency on amo.id = amo_and_agency.amocrm_id
         left join amo_metrics metric on amo.id = metric.amo_id
         left join amo_pipelines pipelines on metric.pipeline_id = pipelines.pipeline_id
         left join amo_pipeline_statuses statuses
                   on statuses.status_id = metric.status_id and statuses.pipeline_id = metric.pipeline_id
where pipelines.pipeline_id = 3245188
  and statuses.status_id = 142
union all
select amo.id,
       amo_and_agency.agencyclients_id                                   agency_client_id,
       'leads'                                                           lead_type,
       metric.utm_source,
       metric.utm_campaign,
       metric.created_at                                                 date,
       date_trunc('week', metric.created_at)::date || ' - ' ||
       (date_trunc('week', metric.created_at) + '6 day'::interval)::date week,
       date_trunc('month', metric.created_at)                            month_,
       to_char(date_trunc('month', metric.created_at), 'YYYY - MONTH')   month_string,
       case
           when metric.utm_campaign ~* 'smm' and metric.utm_source = 'vk_di' THEN 'smm'
           when metric.utm_source = 'vk_di' THEN 'vk_target'
           when metric.utm_campaign ~* 'smm' and utm_source = 'mytarget_di' THEN 'smm'
           when metric.utm_source = 'mytarget_di' THEN 'my_target'
           when metric.utm_campaign ~* 'mkb' THEN 'mkb'
           when metric.utm_campaign ~* 'video' THEN 'video'
           when metric.utm_campaign isnull THEN 'search'
           when metric.utm_campaign ~* 'master' THEN 'master'
           when metric.utm_campaign = 'general_kviz_krd' THEN 'search'
           when metric.utm_campaign ~* 'master_kviz_krd' THEN 'master'
           when metric.utm_campaign ~* 'search' THEN 'search'
           when metric.utm_campaign ~* 'discovery' and utm_source = 'google' THEN 'discovery'
           when metric.utm_campaign ~* 'network' THEN 'network'
           when metric.utm_campaign ~* 'performance_max' and utm_source = 'google' THEN 'performance_max'
           when metric.utm_campaign ~* 'perfomance_max' and utm_source = 'google' THEN 'performance_max'
           END                                                           channel,
       case
           when metric.utm_campaign ~* '_brand' THEN True
           when metric.utm_campaign ~* 'brand_' THEN True
           when metric.utm_campaign ~* '_brand_' THEN True
           else False
           END                                                           is_brand
from amo_crm amo
         left join amo_crm_and_agency_client amo_and_agency on amo.id = amo_and_agency.amocrm_id
         left join amo_metrics metric on amo.id = metric.amo_id
         left join amo_pipelines pipelines on metric.pipeline_id = pipelines.pipeline_id
         left join amo_pipeline_statuses statuses
                   on statuses.status_id = metric.status_id and statuses.pipeline_id = metric.pipeline_id
where pipelines.pipeline_id = 3245188
union all
select amo.id,
       amo_and_agency.agencyclients_id                                   agency_client_id,
       'gk'                                                              lead_type,
       metric.utm_source,
       metric.utm_campaign,
       metric.created_at                                                 date,
       date_trunc('week', metric.created_at)::date || ' - ' ||
       (date_trunc('week', metric.created_at) + '6 day'::interval)::date week,
       date_trunc('month', metric.created_at)                            month_,
       to_char(date_trunc('month', metric.created_at), 'YYYY - MONTH')   month_string,
       case
           when metric.utm_campaign ~* 'smm' and metric.utm_source = 'vk_di' THEN 'smm'
           when metric.utm_source = 'vk_di' THEN 'vk_target'
           when metric.utm_campaign ~* 'smm' and utm_source = 'mytarget_di' THEN 'smm'
           when metric.utm_source = 'mytarget_di' THEN 'my_target'
           when metric.utm_campaign ~* 'mkb' THEN 'mkb'
           when metric.utm_campaign ~* 'video' THEN 'video'
           when metric.utm_campaign isnull THEN 'search'
           when metric.utm_campaign ~* 'master' THEN 'master'
           when metric.utm_campaign ~* 'master_kviz_krd' THEN 'master'
           when metric.utm_campaign = 'general_kviz_krd' THEN 'search'
           when metric.utm_campaign ~* 'video' and utm_source = 'google' THEN 'video'
           when metric.utm_campaign ~* 'search' THEN 'search'
           when metric.utm_campaign ~* 'discovery' and utm_source = 'google' THEN 'discovery'
           when metric.utm_campaign ~* 'network' THEN 'network'
           when metric.utm_campaign ~* 'performance_max' and utm_source = 'google' THEN 'performance_max'
           when metric.utm_campaign ~* 'perfomance_max' and utm_source = 'google' THEN 'performance_max'
           END                                                           channel,
       case
           when metric.utm_campaign ~* '_brand' THEN True
           when metric.utm_campaign ~* 'brand_' THEN True
           when metric.utm_campaign ~* '_brand_' THEN True
           else False
           END                                                           is_brand
from amo_crm amo
         left join amo_crm_and_agency_client amo_and_agency on amo.id = amo_and_agency.amocrm_id
         left join amo_metrics metric on amo.id = metric.amo_id
         left join amo_pipelines pipelines on metric.pipeline_id = pipelines.pipeline_id
         left join amo_pipeline_statuses statuses
                   on statuses.status_id = metric.status_id and statuses.pipeline_id = metric.pipeline_id
where pipelines.pipeline_id = 3245188
  and statuses.status_id in (142, 32860978);
