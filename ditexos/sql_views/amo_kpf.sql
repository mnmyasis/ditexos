create view amo_kpf
as
    select
           amo.id,
           amo_and_agency.agencyclients_id agency_client_id,
           'kpf' lead_type,
           metric.utm_source,
           metric.utm_campaign,
           metric.closed_at date
    from amo_crm amo
        left join amo_crm_and_agency_client amo_and_agency on amo.id = amo_and_agency.amocrm_id
        left join amo_metrics metric on amo.id = metric.amo_id
        left join amo_pipelines pipelines on metric.pipeline_id = pipelines.pipeline_id
        left join amo_pipeline_statuses statuses on statuses.status_id = metric.status_id and statuses.pipeline_id = metric.pipeline_id
    where pipelines.pipeline_id = 3245188 and statuses.status_id = 142
 union all
    select
           amo.id,
           amo_and_agency.agencyclients_id agency_client_id,
           'leads' lead_type,
           metric.utm_source,
           metric.utm_campaign,
           metric.created_at date
    from amo_crm amo
        left join amo_crm_and_agency_client amo_and_agency on amo.id = amo_and_agency.amocrm_id
        left join amo_metrics metric on amo.id = metric.amo_id
        left join amo_pipelines pipelines on metric.pipeline_id = pipelines.pipeline_id
        left join amo_pipeline_statuses statuses on statuses.status_id = metric.status_id and statuses.pipeline_id = metric.pipeline_id
    where pipelines.pipeline_id = 3245188
union all
    select
           amo.id,
           amo_and_agency.agencyclients_id agency_client_id,
           'gk' lead_type,
           metric.utm_source,
           metric.utm_campaign,
           metric.created_at date
    from amo_crm amo
        left join amo_crm_and_agency_client amo_and_agency on amo.id = amo_and_agency.amocrm_id
        left join amo_metrics metric on amo.id = metric.amo_id
        left join amo_pipelines pipelines on metric.pipeline_id = pipelines.pipeline_id
        left join amo_pipeline_statuses statuses on statuses.status_id = metric.status_id and statuses.pipeline_id = metric.pipeline_id
    where pipelines.pipeline_id = 3245188 and statuses.status_id in (142, 32860978);