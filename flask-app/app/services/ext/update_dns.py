import requests, os, sys

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(app_path)

from app.config import CLOUDFLARE_API_TOKEN, DNS_ZONE_ID
from app.services.pushover_alerts import send_alert


domains = [
    {'name': 'tiendafleming.es', 'proxied': True, 'updated': False, 'subdomains': [
                {'name': 'api.tiendafleming.es', 'proxied': True, 'updated': False}, 
                {'name': 'ssh.tiendafleming.es', 'proxied': False, 'updated': False}
            ]
    }
]

errors = []

HEADERS = {
    'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
    'Content-Type': 'application/json'
}


def get_server_ip():
    response = requests.get('https://api.ipify.org?format=json')
    return response.json()['ip']


def get_record_id(domain):
    url = f'https://api.cloudflare.com/client/v4/zones/{DNS_ZONE_ID}/dns_records'
    params = {'name': domain['name']}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    if data['success']:
        return data['result'][0]['id'], data['result'][0]['content'] 
    else:
        errors.append(f'Error obteniendo el ID del registro para {domain['name']}: {data['errors']}.')
        return None


def update_dns_record(record_id, domain, server_ip):
    url = f'https://api.cloudflare.com/client/v4/zones/{DNS_ZONE_ID}/dns_records/{record_id}'
    
    data = {
        'type': 'A',
        'name': domain['name'],
        'content': server_ip,
        'ttl': 1, # auto
        'proxied': domain['proxied']
    }
    response = requests.put(url, headers=HEADERS, json=data)
    data = response.json()
    if data['success']:
        domain['updated'] = True
        
    else:
        errors.append(f'Error actualizando el registro DNS para {domain['name']}: {data['errors']}.')


def send_update_status(changed_ip, server_ip):
    if changed_ip is True:
        alert_content = []
        alert_priority = 0
        
        ip_change_info = f'La IP del server ha cambiado a <b>{server_ip}</b>.\n\n'
        alert_content.append(ip_change_info)
        
        domains_updated = ''
        n_domains_updated = 0
        
        for domain in domains: 
            if domain['updated'] == True:
                n_domains_updated +=1
                domains_updated += f'<font color="#4a99f3">{domain['name']}</font>, '
            
            for subdomain in domain['subdomains']:
                n_domains_updated +=1
                domains_updated += f'<font color="#4a99f3">{subdomain['name']}</font>, '
                
                
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
            alert_content.append('\n<font color="#72df51">Sin errores</font>')
        
        message = ''.join([content for content in alert_content])
        send_alert(message, alert_priority)
        
    
    
def main():
    changed_ip = False
    
    server_ip = get_server_ip()

    main_domain = domains[0]

    main_record_id, record_ip = get_record_id(main_domain)
    
    if main_record_id:
        if server_ip == record_ip:
            changed_ip = False
        else:
            changed_ip = True
            update_dns_record(main_record_id, main_domain, server_ip)
            
            for subdomain in main_domain['subdomains']:
                record_id, ip = get_record_id(subdomain)
                if record_id:
                    update_dns_record(record_id, subdomain, server_ip)
    
    send_update_status(changed_ip, server_ip)
            
        


if __name__ == "__main__":
    main()