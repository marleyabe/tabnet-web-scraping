from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import os

TIMEOUT = 30
MAX_RETRIES = 3

def wait_and_click(driver, xpath):
    el = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    el.click()
    return el

def wait_and_find(driver, xpath):
    return WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

def get_data(meses=13):
    os.makedirs('baixados', exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    driver.get('http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/spabr.def')

    # Esperar o formulário carregar
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="I"]'))
    )

    ## Desselecionar todas as opções
    # Conteudo
    wait_and_click(driver, '//*[@id="I"]/option[1]')
    # mes
    wait_and_click(driver, '//*[@id="A"]/option[1]')

    ## Configurando a página
    # Exibir linhas zeradas
    wait_and_click(driver, '//*[@id="Z"]')
    # Separador ;
    wait_and_click(driver, '/html/body/div/div/center/div/form/div[4]/div[2]/div[1]/div[2]/input[3]')

    for coluna in ['//*[@id="C"]/option[7]', '//*[@id="C"]/option[8]']:
        wait_and_click(driver, coluna)

        for conteudo in ['//*[@id="I"]/option[1]', '//*[@id="I"]/option[2]']:
            wait_and_click(driver, conteudo)
            df_temp = pd.DataFrame()
            for mes in range(1, meses+1):
                wait_and_click(driver, f'//*[@id="A"]/option[{mes}]')
                ano = wait_and_find(driver, f'//*[@id="A"]/option[{mes}]').text

                # Click para mostrar o csv (com retry)
                SUBMIT_XPATH = '/html/body/div/div/center/div/form/div[4]/div[2]/div[2]/input[1]'
                for attempt in range(1, MAX_RETRIES + 1):
                    wait_and_click(driver, SUBMIT_XPATH)

                    WebDriverWait(driver, 60).until(lambda d: len(d.window_handles) > 1)
                    driver.switch_to.window(driver.window_handles[1])

                    try:
                        pre_el = WebDriverWait(driver, 120).until(
                            EC.presence_of_element_located((By.TAG_NAME, 'pre'))
                        )
                        break  # sucesso
                    except TimeoutException:
                        print(f'[WARN] Timeout ao buscar <pre> (tentativa {attempt}/{MAX_RETRIES}), reiniciando...')
                        with open(f'debug_page_{attempt}.html', 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        if attempt == MAX_RETRIES:
                            raise
                else:
                    raise TimeoutException(f'Falhou após {MAX_RETRIES} tentativas')

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Pequena pausa para garantir que todo o texto foi renderizado
                time.sleep(1)
                dados = pre_el.text.split('\n')

                df = pd.DataFrame([x.split(';') for x in dados])
                df['ano'] = ano
                if df_temp.empty:
                    df_temp = df
                else:
                    df_temp = pd.concat([df_temp, df.iloc[1:-1]])

                # voltar para a aba inicial
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                # Esperar a página principal estar pronta novamente
                wait_and_click(driver, f'//*[@id="A"]/option[{mes}]')

            df_temp.to_csv(f'baixados/{wait_and_find(driver, coluna).text}_{wait_and_find(driver, conteudo).text}.csv', index=False, sep=';')

            wait_and_click(driver, conteudo)

## Executa a função indicando o número de meses
if __name__ == '__main__':
    get_data(13)
