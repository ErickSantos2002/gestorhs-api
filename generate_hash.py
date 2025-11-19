#!/usr/bin/env python3
"""
Script para gerar hash bcrypt de uma senha
Uso: python3 generate_hash.py
"""
from app.utils.security import hash_password

senha = "admin123"
hash_gerado = hash_password(senha)

print(f"\n✅ Hash gerado para senha '{senha}':")
print(f"\n{hash_gerado}\n")
print("Execute no banco PostgreSQL:")
print(f"\nUPDATE usuarios SET senha = '{hash_gerado}' WHERE login = 'admin';")
print()
