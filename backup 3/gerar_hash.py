import bcrypt

# 1. Defina a senha que você usará para acessar o Painel Admin
senha_secreta = "Eps@1472".encode('utf-8')

# 2. Gera o hash (criptografia irreversível)
hash_gerado = bcrypt.hashpw(senha_secreta, bcrypt.gensalt()).decode('utf-8')

# 3. Imprime o resultado
print("-" * 50)
print(f"Senha de texto simples: {senha_secreta.decode('utf-8')}")
print(f"COPIE ESTE VALOR para ADMIN_PASSWORD_HASH:")
print(hash_gerado)
print("-" * 50)