import requests, os, sys

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(app_path)

from dotenv import load_dotenv
load_dotenv(os.path.join(app_path, ".env"))

from app.config import CLOUDFLARE_API_TOKEN, DNS_ZONE_ID
from app.services.pushover_alerts import send_alert


domains = [
    {'name': 'tiendafleming.com', 'proxied': True, 'updated': False, 'subdomains':[]}
]

errors = []

HEADERS = {
    'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
    'Content-Type': 'application/json'
}

REQUEST_TIMEOUT = 15


def get_server_ip():
    response = requests.get('https://api.ipify.org?format=json', timeout=REQUEST_TIMEOUT)
    return response.json()['ip']


def parse_cloudflare_response(response):
    try:
        return response.json(), None
    except ValueError:
        body = (response.text or '')[:300]
        return None, f'HTTP {response.status_code}, respuesta no JSON: {body}'


def get_record_id(domain):
    url = f'https://api.cloudflare.com/client/v4/zones/{DNS_ZONE_ID}/dns_records'
    params = {'name': domain['name'], 'type': 'A'}

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        errors.append(f"Error de red obteniendo el ID del registro para {domain['name']}: {exc}.")
        return None, None

    data, parse_error = parse_cloudflare_response(response)
    if parse_error:
        errors.append(f"Error obteniendo el ID del registro para {domain['name']}: {parse_error}.")
        return None, None

    if not data.get('success'):
        errors.append(
            f"Error obteniendo el ID del registro para {domain['name']}: "
            f"HTTP {response.status_code}, {data.get('errors')}."
        )
        return None, None

    results = data.get('result') or []
    if not results:
        errors.append(f"No se encontró el registro DNS A para {domain['name']}.")
        return None, None

    return results[0]['id'], results[0]['content']


def update_dns_record(record_id, domain, server_ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{DNS_ZONE_ID}/dns_records/{record_id}'

    payload = {
        'type': 'A',
        'name': domain['name'],
        'content': server_ip,
        'ttl': 1, # auto
        'proxied': domain['proxied']
    }

    try:
        response = requests.put(url, headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        errors.append(f"Error de red actualizando el registro DNS para {domain['name']}: {exc}.")
        return

    data, parse_error = parse_cloudflare_response(response)
    if parse_error:
        errors.append(f"Error actualizando el registro DNS para {domain['name']}: {parse_error}.")
        return

    if data.get('success'):
        domain['updated'] = True
    else:
        errors.append(
            f"Error actualizando el registro DNS para {domain['name']}: "
            f"HTTP {response.status_code}, {data.get('errors')}."
        )


def send_update_status(changed_ip, server_ip):
    if not changed_ip and not errors:
        return

    alert_content = []
    alert_priority = 0

    if changed_ip:
        ip_change_info = f'La IP del server ha cambiado a <b>{server_ip}</b>.\n\n'
        alert_content.append(ip_change_info)
    elif errors:
        alert_content.append(
            f'Error actualizando DNS. IP del server: <b>{server_ip}</b>.\n\n'
        )

    domains_updated = ''
    n_domains_updated = 0

    for domain in domains:
        if domain['updated'] == True:
            n_domains_updated +=1
            domains_updated += f"<font color='#4a99f3'>{domain['name']}</font>, "

        for subdomain in domain['subdomains']:
            if subdomain.get('updated') == True:
                n_domains_updated +=1
                domains_updated += f"<font color='#4a99f3'>{subdomain['name']}</font>, "


    if n_domains_updated == 0:
        record_updated_info = None
    else:
        domains_updated = domains_updated.rstrip(', ')
        record_updated_info = f'Se han actualizado los siguientes dominios: {domains_updated}\n'
        alert_content.append(record_updated_info)

    if len(errors) != 0:
        errors_info = 'Se han producido los siguientes errores:\n'

        for error in errors:
            errors_info += f'{error}\n'

        alert_content.append(errors_info)

        if n_domains_updated == 0:
            alert_priority = 1
    else:
        alert_content.append("<br>\n<font color='#72df51'>Sin errores</font>")

    message = ''.join([content for content in alert_content])
    send_alert(message, alert_priority)


def main():
    changed_ip = False

    if not CLOUDFLARE_API_TOKEN or not DNS_ZONE_ID:
        errors.append('CLOUDFLARE_API_TOKEN o DNS_ZONE_ID no están definidos en el entorno.')

    server_ip = get_server_ip()
    print(f"Server IP : {server_ip}")

    main_domain = domains[0]

    main_record_id, record_ip = get_record_id(main_domain)

    print(f'Server IP : {server_ip}')
    print(f'Record ID : {main_record_id}')
    print(f'DNS IP    : {record_ip}')

    if main_record_id:
        if server_ip == record_ip:
            print("La IP ya coincide")
            changed_ip = False
        else:
            print("Actualizando...")
            changed_ip = True
            update_dns_record(main_record_id, main_domain, server_ip)

            for subdomain in main_domain['subdomains']:
                record_id, ip = get_record_id(subdomain)
                if record_id:
                    update_dns_record(record_id, subdomain, server_ip)

    if errors:
        print('Errors:')
        for error in errors:
            print(f' - {error}')

    send_update_status(changed_ip, server_ip)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        errors.append(f'Error inesperado en update_dns: {exc}.')
        print(f'Error inesperado: {exc}')
        try:
            send_alert(
                f'Error inesperado actualizando DNS: {exc}',
                1
            )
        except Exception:
            pass
        raise
