# Synoptix Login Automation

Script Python para automação completa do processo de login no sistema Synoptix, incluindo extração automática de código OTP.

## Funcionalidades

- ✅ Abre o navegador automaticamente
- ✅ Navega para a página de login
- ✅ Preenche credenciais automaticamente
- ✅ Extrai código OTP do arquivo .eml mais recente
- ✅ Preenche código OTP nos campos individuais
- ✅ Remove arquivo .eml após uso
- ✅ Mostra ícone de cachorro no final 🐕

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Certifique-se de ter o Chrome instalado no seu sistema

## Uso

Execute o script:
```bash
python synoptix-login-automation.py
```

## Configuração

O script está configurado para:
- **URL**: `http://localhost:5173/login`
- **Email**: `Synoptix.Admin@one-beyond.com`
- **Senha**: `Password!23`
- **Diretório de emails**: `/tmp/mailroot/Synoptix/`

## Como funciona

1. Abre o navegador Chrome
2. Navega para a página de login
3. Preenche email e senha
4. Clica no botão Login
5. Aguarda redirecionamento para página de OTP
6. Lê o arquivo .eml mais recente em `/tmp/mailroot/Synoptix/`
7. Extrai o código OTP de 6 dígitos
8. Remove o arquivo .eml
9. Preenche o código OTP nos 6 campos individuais
10. Clica em Verify
11. Mostra ícone de cachorro 🐕

## Requisitos

- Python 3.7+
- Chrome browser
- Arquivos .eml em `/tmp/mailroot/Synoptix/`
