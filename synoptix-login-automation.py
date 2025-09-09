#!/usr/bin/env python3
"""
Script de automação para login no Synoptix
Automatiza o processo completo: login, extração de OTP e verificação
"""

import time
import re
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SynoptixLoginAutomation:
    def __init__(self):
        self.driver = None
        self.email = "Synoptix.Admin@one-beyond.com"
        self.password = "Password!23"
        self.login_url = "http://localhost:5173/login"
        self.otp_url = "http://localhost:5173/login/verify-otp"
        self.mail_dir = "/tmp/mailroot/Synoptix/"
        
    def setup_driver(self, headless=False, keep_open=False):
        """Configura o driver do Chrome"""
        chrome_options = Options()
        
        # Configurações básicas
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configurações adicionais para melhor experiência
        chrome_options.add_argument("--start-maximized")  # Abre maximizado
        chrome_options.add_argument("--disable-notifications")  # Desabilita notificações
        chrome_options.add_argument("--disable-popup-blocking")  # Desabilita bloqueio de popups
        
        # Modo headless (sem interface gráfica)
        if headless:
            chrome_options.add_argument("--headless")
            print("🔍 Modo headless ativado (sem interface gráfica)")
        
        # Manter navegador aberto após execução
        if keep_open:
            chrome_options.add_experimental_option("detach", True)
            print("🔒 Navegador será mantido aberto após execução")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Navegador Chrome iniciado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar o navegador: {e}")
            print("💡 Certifique-se de que o Chrome está instalado no seu sistema")
            return False
    
    def navigate_to_login(self):
        """Navega para a página de login"""
        try:
            print(f"🌐 Navegando para {self.login_url}")
            self.driver.get(self.login_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            print("✅ Página de login carregada")
            return True
        except TimeoutException:
            print("❌ Timeout ao carregar página de login")
            return False
    
    def fill_login_credentials(self):
        """Preenche as credenciais de login"""
        try:
            print("📝 Preenchendo credenciais...")
            
            # Campo de email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            print(f"✅ Email inserido: {self.email}")
            
            # Campo de senha
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            print("✅ Senha inserida")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao preencher credenciais: {e}")
            return False
    
    def click_login_button(self):
        """Clica no botão de login"""
        try:
            print("🔘 Clicando no botão Login...")
            
            # Procura pelo botão de login (pode ser span ou button)
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Login')] | //button[contains(text(), 'Login')]"))
            )
            login_button.click()
            print("✅ Botão Login clicado")
            
            # Aguarda redirecionamento para página de OTP
            WebDriverWait(self.driver, 15).until(
                lambda driver: self.otp_url in driver.current_url
            )
            print("✅ Redirecionado para página de verificação OTP")
            return True
            
        except TimeoutException:
            print("❌ Timeout ao clicar no botão de login ou redirecionamento")
            return False
        except Exception as e:
            print(f"❌ Erro ao clicar no botão de login: {e}")
            return False
    
    def extract_otp_from_email(self):
        """Extrai o código OTP do arquivo .eml mais recente"""
        try:
            print("📧 Procurando arquivos .eml...")
            
            # Lista todos os arquivos .eml no diretório
            eml_files = glob.glob(os.path.join(self.mail_dir, "*.eml"))
            
            if not eml_files:
                print("❌ Nenhum arquivo .eml encontrado")
                return None
            
            # Pega o arquivo mais recente
            latest_eml = max(eml_files, key=os.path.getctime)
            print(f"📄 Lendo arquivo mais recente: {latest_eml}")
            
            # Lê o conteúdo do arquivo
            with open(latest_eml, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extrai o código OTP usando regex
            otp_pattern = r'<strong[^>]*>(\d{6})</strong>'
            match = re.search(otp_pattern, content)
            
            if match:
                otp_code = match.group(1)
                print(f"✅ Código OTP extraído: {otp_code}")
                
                # Remove o arquivo .eml após extrair o código
                os.remove(latest_eml)
                print("🗑️ Arquivo .eml removido")
                
                return otp_code
            else:
                print("❌ Código OTP não encontrado no arquivo")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao extrair OTP: {e}")
            return None
    
    def fill_otp_code(self, otp_code):
        """Preenche o código OTP nos campos individuais"""
        try:
            print(f"🔢 Preenchendo código OTP: {otp_code}")
            
            # Aguarda os campos OTP carregarem
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "otp-input"))
            )
            
            # Encontra todos os campos de input OTP
            otp_inputs = self.driver.find_elements(By.CLASS_NAME, "otp-input")
            
            if len(otp_inputs) != 6:
                print(f"❌ Esperado 6 campos OTP, encontrado {len(otp_inputs)}")
                return False
            
            # Preenche cada campo com um dígito
            for i, digit in enumerate(otp_code):
                if i < len(otp_inputs):
                    otp_inputs[i].clear()
                    otp_inputs[i].send_keys(digit)
                    time.sleep(0.1)  # Pequena pausa entre os campos
            
            print("✅ Código OTP preenchido")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao preencher código OTP: {e}")
            return False
    
    def click_verify_button(self):
        """Clica no botão de verificação"""
        try:
            print("🔘 Clicando no botão Verify...")
            
            # Procura pelo botão de verificação
            verify_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Verify')] | //span[contains(text(), 'Verify')]"))
            )
            verify_button.click()
            print("✅ Botão Verify clicado")
            
            # Aguarda um pouco para ver se há redirecionamento
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ Erro ao clicar no botão Verify: {e}")
            return False
    
    def show_dog_icon(self):
        """Mostra ícone de cachorro"""
        print("\n" + "="*50)
        print("🐕 LOGIN CONCLUÍDO COM SUCESSO! 🐕")
        print("="*50)
        print("""
    🐕‍🦺
   /|\\_/|
  /_/  \\_\\
  |  \\_/  |
  \\_/ \\_/
    """)
        print("🎉 Automação finalizada! O usuário está logado no sistema.")
        print("="*50)
    
    def run_automation(self, headless=False, keep_open=False):
        """Executa todo o processo de automação"""
        print("🚀 Iniciando automação do login Synoptix...")
        print("="*50)
        
        try:
            # 1. Configurar navegador
            if not self.setup_driver(headless=headless, keep_open=keep_open):
                return False
            
            # 2. Navegar para login
            if not self.navigate_to_login():
                return False
            
            # 3. Preencher credenciais
            if not self.fill_login_credentials():
                return False
            
            # 4. Clicar em login
            if not self.click_login_button():
                return False
            
            # 5. Extrair OTP do email
            otp_code = self.extract_otp_from_email()
            if not otp_code:
                return False
            
            # 6. Preencher código OTP
            if not self.fill_otp_code(otp_code):
                return False
            
            # 7. Clicar em verify
            if not self.click_verify_button():
                return False
            
            # 8. Mostrar ícone de cachorro
            self.show_dog_icon()
            
            # Manter o navegador aberto por alguns segundos (se não for keep_open)
            if not keep_open:
                print("⏳ Mantendo navegador aberto por 5 segundos...")
                time.sleep(5)
            else:
                print("🔒 Navegador será mantido aberto conforme solicitado")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante a automação: {e}")
            return False
        
        finally:
            if self.driver and not keep_open:
                print("🔒 Fechando navegador...")
                self.driver.quit()
            elif self.driver and keep_open:
                print("🔒 Navegador mantido aberto para uso manual")

def main():
    """Função principal"""
    import sys
    
    # Verifica argumentos da linha de comando
    headless = "--headless" in sys.argv
    keep_open = "--keep-open" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
🚀 Synoptix Login Automation

Uso: python3 synoptix-login-automation.py [opções]

Opções:
  --headless     Executa sem interface gráfica (modo invisível)
  --keep-open    Mantém o navegador aberto após a execução
  --help, -h     Mostra esta ajuda

Exemplos:
  python3 synoptix-login-automation.py                    # Modo normal
  python3 synoptix-login-automation.py --headless         # Modo invisível
  python3 synoptix-login-automation.py --keep-open        # Mantém navegador aberto
  python3 synoptix-login-automation.py --headless --keep-open  # Ambos
        """)
        return
    
    automation = SynoptixLoginAutomation()
    success = automation.run_automation(headless=headless, keep_open=keep_open)
    
    if success:
        print("\n✅ Automação executada com sucesso!")
    else:
        print("\n❌ Automação falhou!")

if __name__ == "__main__":
    main()
