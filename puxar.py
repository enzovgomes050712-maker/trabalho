from flask import Flask, render_template, request, jsonify
import requests
import random
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- LISTA COMPLETA DE USER-AGENTS ---
ua_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.80 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
]

# --- TODAS AS PLATAFORMAS DO SEU PROJETO ---
PLATFORMS = {
    "Instagram": "https://www.instagram.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "GitHub": "https://github.com/{}",
    "Roblox": "https://www.roblox.com/search/users?keyword={}",
    "Twitch": "https://www.twitch.tv/{}",
    "Twitter": "https://twitter.com/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Gmail (Check)": "https://mail.google.com/mail/gxlu?email={}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Reddit": "https://www.reddit.com/user/{}"
}

def check_platform(username, platform, url):
    headers = {'User-Agent': random.choice(ua_list)}
    target = url.format(username)
    try:
        # Request simples para checar se o perfil existe
        response = requests.get(target, headers=headers, timeout=8)
        
        # Log no terminal para você ver o que está acontecendo
        print(f"[DEBUG] {platform}: Status {response.status_code}")
        
        if response.status_code == 200:
            return f"[+] {platform}: {target}"
    except Exception as e:
        print(f"[ERRO] {platform}: {e}")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    target = data.get('username').strip()
    results = []

    # --- LÓGICA PARA IP ---
    # Verifica se o alvo tem pontos e números (formato de IP)
# --- LÓGICA PARA IP (ESTILO GRABIFY) ---
    if target.replace('.', '').isdigit() and target.count('.') == 3:
        print(f"\n> [!] Investigando Infraestrutura: {target}")
        try:
            # Aqui adicionamos os campos extras: proxy, hosting e mobile
            campos = "status,message,country,city,regionName,isp,proxy,hosting,mobile,org"
            response = requests.get(f"http://ip-api.com/json/{target}?fields={campos}").json()
            
            if response['status'] == 'success':
                results.append(f"--- RELATÓRIO DE IP DETECTADO ---")
                results.append(f"[LOCAL] {response.get('city')}, {response.get('regionName')} - {response.get('country')}")
                results.append(f"[PROVEDOR] {response.get('isp')}")
                
                # Identificação de Proxy/VPN (Igual ao Grabify)
                proxy = "SIM (VPN/Proxy)" if response.get('proxy') else "NÃO (Residencial)"
                hosting = "SIM (Servidor/Data Center)" if response.get('hosting') else "NÃO"
                results.append(f"[PROXY/VPN] {proxy}")
                results.append(f"[HOSTING] {hosting}")
                
                # Identifica se é rede móvel (celular) ou Wi-Fi
                tipo = "Móvel (4G/5G)" if response.get('mobile') else "Rede Fixa/Wi-Fi"
                results.append(f"[TIPO DE REDE] {tipo}")
                
                results.append(f"[ORGANIZAÇÃO] {response.get('org')}")
            else:
                results.append(f"[!] IP Inválido ou não encontrado.")
        except:
            results.append("[!] Erro ao conectar com o banco de dados de IP.")

    # --- LÓGICA PARA NOME DE USUÁRIO (O que já tínhamos) ---
    else:
        print(f"\n> Iniciando varredura de Redes Sociais para: {target}")
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(check_platform, target, p, u) for p, u in PLATFORMS.items()]
            for future in futures:
                res = future.result()
                if res:
                    results.append(res)

    if not results:
        results.append("[-] Nenhum dado encontrado para este alvo.")
        
    return jsonify({"results": results})

if __name__ == '__main__':
    # Roda o servidor. IMPORTANTE: Use o link http://127.0.0.1:5000 que aparecer
    app.run(debug=True, port=5000)