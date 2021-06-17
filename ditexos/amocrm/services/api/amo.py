import os

from requests import post, get
import json
import pandas as pd
from amocrm.models import AmoCRM


def update_refresh_token(referer):
    url = 'https://{}/oauth2/access_token'.format(referer)
    token = AmoCRM.objects.get(subdomain=referer)
    body = {
        "client_id": os.environ.get('AMO_CLIENT_ID'),
        "client_secret": os.environ.get('AMO_CLIENT_SECRET'),
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
        "redirect_uri": "http://localhost.ru:8011/amocrm/allow/"
    }
    headers = {
        'Content-Type': 'application/json'
    }
    json_body = json.dumps(body, ensure_ascii=False).encode('utf8')
    result = post(url, json_body, headers=headers).json()
    access_token = result.get('access_token')
    refresh_token = result.get('refresh_token')
    token.access_token = access_token
    token.refresh_token = refresh_token
    token.save()
    return token


def get_links(id_leads, referer, headers):
    contact_id = []
    for id_lead in id_leads.iloc:
        url = 'https://{}/api/v4/leads/{}/links'.format(referer, id_lead)
        links = get(url, headers=headers).json()
        links = pd.DataFrame(links['_embedded']['links'])
        contact_id.append(links[links.to_entity_type == 'contacts']['to_entity_id'].iloc[0])
    return contact_id


def get_contact(id_contacts, referer, headers):
    contacts = []
    for id_contact in id_contacts:
        url = 'https://{}/api/v4/contacts/{}'.format(referer, id_contact)
        contact = get(url, headers=headers).json()
        contact = pd.DataFrame(contact['custom_fields_values'])
        contacts.append(contact[contact.field_code == 'PHONE']['values'].iloc[0][0]['value'])
    return contacts


def table(referer, access_token):
    url = 'https://{}/api/v4/leads'.format(referer)
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }
    result = get(url, headers=headers).json()
    if result.get('status') == 401:
        token = update_refresh_token(referer)
        headers['Authorization'] = 'Bearer {}'.format(token.access_token)
        result = get(url, headers=headers).json()
    result = pd.DataFrame(result['_embedded']['leads'])
    result['link'] = get_links(result['id'], referer, headers)
    result['contacts'] = get_contact(result['link'], referer, headers)
    # https://mnmyasis.amocrm.ru/api/v4/leads/44581/links
    return result
