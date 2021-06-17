import os
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd

PAGE_SIZE = 100


def report_default(client, customer_id):
    report = []
    ga_service = client.get_service("GoogleAdsService")
    query = """
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                campaign.id,
                campaign.name,
                campaign.status,
                metrics.average_cost,
                metrics.average_cpc,
                metrics.clicks,
                metrics.conversions,
                metrics.cost_micros,
                metrics.ctr,
                metrics.impressions,
                metrics.search_rank_lost_impression_share,
                segments.date
            FROM keyword_view 
            WHERE
                customer.id = {}
                AND segments.year > 2018
                AND segments.year < {}
            """.format(customer_id, datetime.now().year)
    search_request = client.get_type("SearchGoogleAdsStreamRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    response = ga_service.search_stream(search_request)
    for batch in response:
        for row in batch.results:
            res = {
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'ad_group_status': row.ad_group.status,
                'ad_group_criterion_criterion_id': row.ad_group_criterion.criterion_id,
                'ad_group_criterion_keyword_text': row.ad_group_criterion.keyword.text,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'campaign_status': row.campaign.status,
                'metrics_average_cost': row.metrics.average_cost,
                'metrics_clicks': row.metrics.clicks,
                'metrics_conversions': row.metrics.conversions,
                'metrics_cost_micros': row.metrics.cost_micros,
                'metrics_ctr': row.metrics.ctr,
                'metrics_impressions': row.metrics.impressions,
                'metrics_search_rank_lost_impression_share': row.metrics.search_rank_lost_impression_share,
                'segments_date': row.segments.date
            }
            report.append(res)
    df = pd.DataFrame(report)
    return df


def campaigns(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")
    result = []
    query = """
            SELECT
              campaign.id,
              campaign.name,
              campaign.status
            FROM campaign
            ORDER BY campaign.id"""

    # Issues a search request using streaming.
    response = ga_service.search_stream(customer_id=customer_id, query=query)

    for batch in response:
        for row in batch.results:
            print(
                f"Campaign with ID {row.campaign.id} and name "
                f'"{row.campaign.name}" was found.'
            )
            result.append({
                'id': row.campaign.id,
                'name': row.campaign.name,
                'status': row.campaign.status
            })
    return result


def clients(client, customer_id):
    result = []
    googleads_service = client.get_service("GoogleAdsService")
    query = """
            SELECT
              customer_client.client_customer,
              customer_client.level,
              customer_client.manager,
              customer_client.descriptive_name,
              customer_client.currency_code,
              customer_client.time_zone,
              customer_client.id
            FROM customer_client
            WHERE customer_client.level = 1"""

    response = googleads_service.search(
        customer_id=customer_id, query=query
    )

    # Iterates over all rows in all pages to get all customer
    # clients under the specified customer's hierarchy.
    for googleads_row in response:
        customer_client = googleads_row.customer_client
        print(customer_client)
        print(customer_client.descriptive_name)
        result.append({
            'name': customer_client.descriptive_name,
            'id': customer_client.id
        })
    return result


if __name__ == '__main__':
    developer_token = os.environ.get('GOOGLE_DEVELOPER_TOKEN')
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    credentials = {
        "developer_token": developer_token,
        "refresh_token": "1//0cpdyqt1j7wY-CgYIARAAGAwSNwF-L9IrRUpFayo7lDGL6wq9GkTmW6qlKsvMycOtRB2DCTVUFEhPZen22C1WCGdEvPhcZpRv6PQ",
        "client_id": client_id,
        "client_secret": client_secret,
        "login_customer_id": "7406582103"
    }
    googleads_client = GoogleAdsClient.load_from_dict(credentials)
    report_default(googleads_client, '6597569511')
