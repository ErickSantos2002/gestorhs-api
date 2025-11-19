#!/usr/bin/env python3
"""
Script para testar CORS da API
"""
import requests
import sys


def test_cors(api_url: str, origin: str):
    """Testa se CORS esta funcionando"""

    print(f"\n🧪 Testando CORS da API")
    print(f"📍 API: {api_url}")
    print(f"🌐 Origin: {origin}\n")

    # Teste 1: Health check detalhado
    print("1️⃣  Verificando configuracao CORS...")
    try:
        response = requests.get(f"{api_url}/health/detailed")
        if response.status_code == 200:
            data = response.json()
            health = data.get("health", {})

            print(f"   ✅ API respondendo: {response.status_code}")
            print(f"   📋 CORS configurado (raw): {health.get('cors_origins_raw')}")
            print(f"   📋 CORS configurado (list): {health.get('cors_origins_list')}")
            print(f"   🐛 Debug mode: {health.get('debug')}")
            print(f"   💾 Database: {health.get('database')}")
            print(f"   📊 Fases OS: {health.get('fases_os')}")

            # Verificar se origin esta na lista
            origins = health.get('cors_origins_list', [])
            if origin in origins:
                print(f"\n   ✅ Origin '{origin}' ESTA na lista de CORS!")
            else:
                print(f"\n   ❌ Origin '{origin}' NAO ESTA na lista de CORS!")
                print(f"   ⚠️  Origens permitidas: {origins}")
        else:
            print(f"   ❌ Erro: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        return False

    # Teste 2: Preflight OPTIONS
    print(f"\n2️⃣  Testando preflight (OPTIONS)...")
    try:
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options(f"{api_url}/api/v1/auth/login", headers=headers)

        print(f"   📤 Status: {response.status_code}")

        # Verificar headers CORS na resposta
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        cors_methods = response.headers.get("Access-Control-Allow-Methods")
        cors_headers = response.headers.get("Access-Control-Allow-Headers")
        cors_credentials = response.headers.get("Access-Control-Allow-Credentials")

        if cors_origin:
            print(f"   ✅ Access-Control-Allow-Origin: {cors_origin}")
        else:
            print(f"   ❌ Access-Control-Allow-Origin: AUSENTE!")

        if cors_methods:
            print(f"   ✅ Access-Control-Allow-Methods: {cors_methods}")
        else:
            print(f"   ⚠️  Access-Control-Allow-Methods: AUSENTE")

        if cors_headers:
            print(f"   ✅ Access-Control-Allow-Headers: {cors_headers}")
        else:
            print(f"   ⚠️  Access-Control-Allow-Headers: AUSENTE")

        if cors_credentials:
            print(f"   ✅ Access-Control-Allow-Credentials: {cors_credentials}")

        if response.status_code == 200 and cors_origin:
            print(f"\n   ✅ CORS funcionando! Preflight passou.")
            return True
        else:
            print(f"\n   ❌ CORS NAO funcionando corretamente!")
            return False

    except Exception as e:
        print(f"   ❌ Erro ao testar preflight: {e}")
        return False


def main():
    """Main"""
    # Configurar API e Origin
    api_url = "https://gestorhsapi.healthsafetytech.com"
    origin = "https://gestorhs.healthsafetytech.com"

    # Permitir passar URL por argumento
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    if len(sys.argv) > 2:
        origin = sys.argv[2]

    # Testar
    success = test_cors(api_url, origin)

    # Resultado final
    print("\n" + "="*60)
    if success:
        print("✅ CORS FUNCIONANDO CORRETAMENTE!")
    else:
        print("❌ CORS COM PROBLEMAS!")
        print("\n🔧 Solucoes:")
        print("   1. Verifique se o .env no servidor tem:")
        print(f"      CORS_ORIGINS=...,{origin}")
        print("   2. Reinicie a API")
        print("   3. Rode este teste novamente")
    print("="*60 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
