import os
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd

PAGE_SIZE = 100


def report_keyword(client, customer_id, start_date, end_date):
    report = []
    ga_service = client.get_service("GoogleAdsService", version="v7")
    query = """
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                campaign.id,
                campaign.name,
                metrics.clicks,
                metrics.cost_micros,
                metrics.impressions,
                segments.date
            FROM keyword_view 
            WHERE
                segments.date >= '{}'
                AND segments.date <= '{}'
            """.format(start_date, end_date)
    search_request = client.get_type("SearchGoogleAdsStreamRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    response = ga_service.search_stream(search_request)
    for batch in response:
        for row in batch.results:
            res = {
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'ad_group_criterion_criterion_id': row.ad_group_criterion.criterion_id,
                'ad_group_criterion_keyword_text': row.ad_group_criterion.keyword.text,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'metrics_clicks': row.metrics.clicks,
                'metrics_cost_micros': row.metrics.cost_micros,
                'metrics_impressions': row.metrics.impressions,
                'segments_date': row.segments.date
            }
            report.append(res)
    df = pd.DataFrame(report)
    df.to_excel('google_ads_{}.xlsx'.format(datetime.now().strftime('%Y_%m_%d')))
    return df


def report_campaign(client, customer_id, start_date, end_date):
    report = []
    ga_service = client.get_service("GoogleAdsService", version="v7")
    query = f"""
            SELECT
              campaign.id,
              campaign.name,
              metrics.impressions,
              metrics.clicks,
              metrics.cost_micros,
              segments.date
            FROM campaign WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
            """
    search_request = client.get_type("SearchGoogleAdsStreamRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    response = ga_service.search_stream(search_request)
    for batch in response:
        for row in batch.results:
            res = {
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'metrics_clicks': row.metrics.clicks,
                'metrics_cost_micros': row.metrics.cost_micros,
                'metrics_impressions': row.metrics.impressions,
                'segments_date': row.segments.date
            }
            report.append(res)
    df = pd.DataFrame(report)
    df.to_excel('google_ads_{}.xlsx'.format(datetime.now().strftime('%Y_%m_%d')))
    return df


def clients(client, customer_id, customer_client_level):
    result = []
    googleads_service = client.get_service("GoogleAdsService")
    query = f"""
            SELECT
              customer_client.client_customer,
              customer_client.level,
              customer_client.manager,
              customer_client.descriptive_name,
              customer_client.currency_code,
              customer_client.time_zone,
              customer_client.id
            FROM customer_client
            WHERE customer_client.level = {customer_client_level}"""

    response = googleads_service.search(
        customer_id=customer_id,
        query=query
    )
    for googleads_row in response:
        customer_client = googleads_row.customer_client
        print(customer_client)
        print(customer_client.descriptive_name)
        result.append({
            'name': customer_client.descriptive_name,
            'id': customer_client.id
        })
    return result
