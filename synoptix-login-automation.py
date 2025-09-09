#!/usr/bin/env python3

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

class LoginAutomation:
    def __init__(self):
        self.driver = None
        self.email = "Synoptix.Admin@one-beyond.com"
        self.password = "Password!23"
        self.login_url = "http://localhost:5173/login"
        self.otp_url = "http://localhost:5173/login/verify-otp"
        self.mail_dir = "/tmp/mailroot/Synoptix/"
        
    def setup_driver(self, headless=False, keep_open=False):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        if headless:
            chrome_options.add_argument("--headless")
            print("🔍 Modo headless ativado")
        
        if keep_open:
            chrome_options.add_experimental_option("detach", True)
            print("🔒 Navegador será mantido aberto")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Navegador iniciado")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar navegador: {e}")
            return False
    
    def navigate_to_login(self):
        try:
            print(f"🌐 Navegando para {self.login_url}")
            self.driver.get(self.login_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            print("✅ Página carregada")
            return True
        except TimeoutException:
            print("❌ Timeout ao carregar página")
            return False
    
    def fill_login_credentials(self):
        try:
            print("📝 Preenchendo credenciais...")
            
            email_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            print(f"✅ Email inserido: {self.email}")
            
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            print("✅ Senha inserida")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao preencher credenciais: {e}")
            return False
    
    def click_login_button(self):
        try:
            print("🔘 Clicando no botão Login...")
            
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Login')] | //button[contains(text(), 'Login')]"))
            )
            login_button.click()
            print("✅ Botão Login clicado")
            
            WebDriverWait(self.driver, 15).until(
                lambda driver: self.otp_url in driver.current_url
            )
            print("✅ Redirecionado para página OTP")
            return True
            
        except TimeoutException:
            print("❌ Timeout ao clicar no botão ou redirecionamento")
            return False
        except Exception as e:
            print(f"❌ Erro ao clicar no botão: {e}")
            return False
    
    def extract_otp_from_email(self):
        try:
            print("📧 Procurando arquivos .eml...")
            
            eml_files = glob.glob(os.path.join(self.mail_dir, "*.eml"))
            
            if not eml_files:
                print("❌ Nenhum arquivo .eml encontrado")
                return None
            
            latest_eml = max(eml_files, key=os.path.getctime)
            print(f"📄 Lendo arquivo: {latest_eml}")
            
            with open(latest_eml, 'r', encoding='utf-8') as file:
                content = file.read()
            
            otp_pattern = r'<strong[^>]*>(\d{6})</strong>'
            match = re.search(otp_pattern, content)
            
            if match:
                otp_code = match.group(1)
                print(f"✅ Código OTP extraído: {otp_code}")
                
                os.remove(latest_eml)
                print("🗑️ Arquivo .eml removido")
                
                return otp_code
            else:
                print("❌ Código OTP não encontrado")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao extrair OTP: {e}")
            return None
    
    def fill_otp_code(self, otp_code):
        try:
            print(f"🔢 Preenchendo código OTP: {otp_code}")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "otp-input"))
            )
            
            otp_inputs = self.driver.find_elements(By.CLASS_NAME, "otp-input")
            
            if len(otp_inputs) != 6:
                print(f"❌ Esperado 6 campos OTP, encontrado {len(otp_inputs)}")
                return False
            
            for i, digit in enumerate(otp_code):
                if i < len(otp_inputs):
                    otp_inputs[i].clear()
                    otp_inputs[i].send_keys(digit)
                    time.sleep(0.1)
            
            print("✅ Código OTP preenchido")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao preencher código OTP: {e}")
            return False
    
    def click_verify_button(self):
        try:
            print("🔘 Clicando no botão Verify...")
            
            verify_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Verify')] | //span[contains(text(), 'Verify')]"))
            )
            verify_button.click()
            print("✅ Botão Verify clicado")
            
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ Erro ao clicar no botão Verify: {e}")
            return False
    
    def show_dog_icon(self):
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
        print("🎉 Automação finalizada!")
        print("="*50)
    
    def run_automation(self, headless=False, keep_open=False):
        print("🚀 Iniciando automação...")
        print("="*50)
        
        try:
            if not self.setup_driver(headless=headless, keep_open=keep_open):
                return False
            
            if not self.navigate_to_login():
                return False
            
            if not self.fill_login_credentials():
                return False
            
            if not self.click_login_button():
                return False
            
            otp_code = self.extract_otp_from_email()
            if not otp_code:
                return False
            
            if not self.fill_otp_code(otp_code):
                return False
            
            if not self.click_verify_button():
                return False
            
            self.show_dog_icon()
            
            if not keep_open:
                print("⏳ Mantendo navegador aberto por 5 segundos...")
                time.sleep(5)
            else:
                print("🔒 Navegador será mantido aberto")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante a automação: {e}")
            return False
        
        finally:
            if self.driver and not keep_open:
                print("🔒 Fechando navegador...")
                self.driver.quit()
            elif self.driver and keep_open:
                print("🔒 Navegador mantido aberto")

def main():
    import sys
    
    headless = "--headless" in sys.argv
    keep_open = "--keep-open" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
🚀 Login Automation

Uso: python3 synoptix-login-automation.py [opções]

Opções:
  --headless     Executa sem interface gráfica
  --keep-open    Mantém o navegador aberto
  --help, -h     Mostra esta ajuda

Exemplos:
  python3 synoptix-login-automation.py                    # Modo normal
  python3 synoptix-login-automation.py --headless         # Modo invisível
  python3 synoptix-login-automation.py --keep-open        # Mantém navegador aberto
  python3 synoptix-login-automation.py --headless --keep-open  # Ambos
        """)
        return
    
    automation = LoginAutomation()
    success = automation.run_automation(headless=headless, keep_open=keep_open)
    
    if success:
        print("\n✅ Automação executada com sucesso!")
    else:
        print("\n❌ Automação falhou!")

if __name__ == "__main__":
    main()
