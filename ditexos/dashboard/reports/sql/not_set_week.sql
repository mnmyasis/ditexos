SELECT SUB_DATE.utm_source channel,
       SUB_DATE.week       week,
       CASE
           WHEN SUB_LEADS.leads ISNULL THEN 0
           ELSE SUB_LEADS.leads
           END             leads,
       CASE
           WHEN SUB_KPF.leads ISNULL THEN 0
           ELSE SUB_KPF.leads
           END             kpf,
       CASE
           WHEN SUB_GK.leads ISNULL THEN 0
           ELSE SUB_GK.leads
           END             gk
FROM (
         SELECT week,
                CASE
                    WHEN utm_source ISNULL THEN 'not_set'
                    ELSE utm_source
                    END utm_source
         FROM amo_kpf
         WHERE agency_client_id = {agency_client_id}
           AND (utm_source NOT IN ('yandex'
             , 'google'
             , 'mytarget_di'
             , 'vk_di')
            OR
             utm_source ISNULL)
         GROUP BY week, utm_source
     ) SUB_DATE
         LEFT JOIN

     (
         SELECT COUNT(*) leads,
                week,
                CASE
                    WHEN utm_source ISNULL THEN 'not_set'
                    ELSE utm_source
                    END  utm_source
         FROM amo_kpf
         WHERE agency_client_id = {agency_client_id}
           AND lead_type = 'leads'
           AND (utm_source NOT IN ('yandex'
             , 'google'
             , 'mytarget_di'
             , 'vk_di')
            OR
             utm_source ISNULL)
         GROUP BY week, utm_source
     ) SUB_LEADS ON SUB_DATE.week = SUB_LEADS.week
         AND SUB_DATE.utm_source = SUB_LEADS.utm_source
         LEFT JOIN
     (
         SELECT COUNT(*) leads,
                week,
                CASE
                    WHEN utm_source ISNULL THEN 'not_set'
                    ELSE utm_source
                    END  utm_source
         FROM amo_kpf
         WHERE agency_client_id = {agency_client_id}
           AND lead_type = 'kpf'
           AND (utm_source NOT IN ('yandex'
             , 'google'
             , 'mytarget_di'
             , 'vk_di')
            OR
             utm_source ISNULL)
         GROUP BY week, utm_source
     ) SUB_KPF ON SUB_DATE.week = SUB_KPF.week
         AND SUB_DATE.utm_source = SUB_KPF.utm_source
         LEFT JOIN
     (
         SELECT COUNT(*) leads,
                week,
                CASE
                    WHEN utm_source ISNULL THEN 'not_set'
                    ELSE utm_source
                    END  utm_source
         FROM amo_kpf
         WHERE agency_client_id = {agency_client_id}
           AND lead_type = 'gk'
           AND (utm_source NOT IN ('yandex'
             , 'google'
             , 'mytarget_di'
             , 'vk_di')
            OR
             utm_source ISNULL)
         GROUP BY week, utm_source
     ) SUB_GK ON SUB_DATE.week = SUB_GK.week
         AND SUB_DATE.utm_source = SUB_GK.utm_source
ORDER BY SUB_DATE.week DESC;