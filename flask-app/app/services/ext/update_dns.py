import requests, os, sys

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(app_path)

from app.config import CLOUDFLARE_API_TOKEN, DNS_ZONE_ID

HEADERS = {
    'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
    'Content-Type': 'application/json'
}

def get_server_ip():
    response = requests.get('https://api.ipify.org?format=json')
    return response.json()['ip']

def obtener_dns_record_id(domain):
    url = f"https://api.cloudflare.com/client/v4/zones/{DNS_ZONE_ID}/dns_records"
    params = {'name': domain}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    if data['success']:
        return data['result'][0]['id'], data['result'][0]['content'] 
    else:
        print(f"Error obteniendo el ID del registro para {domain}: {data['errors']}")
        return None

def actualizar_dns_record(record_id, domain, current_server_ip, current_record_ip):
    url = f"https://api.cloudflare.com/client/v4/zones/{DNS_ZONE_ID}/dns_records/{record_id}"
    
    if current_server_ip == current_record_ip:
        print('La IP del registro ya está actualizada')

    if domain == 'ssh.tiendafleming.es':
        proxied = False
    else: proxied = True
    
    data = {
        'type': 'A',
        'name': domain,
        'content': current_server_ip,
        'ttl': 1, # auto
        'proxied': proxied
    }
    response = requests.put(url, headers=HEADERS, json=data)
    data = response.json()
    if data['success']:
        print(f"Registro DNS para {domain} actualizado con éxito.")
    else:
        print(f"Error actualizando el registro DNS para {domain}: {data['errors']}")


def main():
    domains = ['tiendafleming.es', 'api.tiendafleming.es', 'ssh.tiendafleming.es']

    current_server_ip = get_server_ip()
    print(f"Current public IP: {current_server_ip}")

    for domain in domains:
        record_id, current_record_ip = obtener_dns_record_id(domain)
        if record_id:
            actualizar_dns_record(record_id, domain, current_server_ip, current_record_ip)
        

if __name__ == "__main__":
    main()