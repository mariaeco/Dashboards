from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from openpyxl import Workbook
import time
import re
import math


start_time = time.time()  # Início da contagem
YEARS = ["2022"]# 

# Função para salvar os dados em uma planilha Excel
def salvar_dados_excel(dados, planilha):
    try:
        # Adicionar os dados à planilha
        planilha.append(dados)
        print("Dados salvos na planilha.")
    except Exception as e:
        print(f"Erro ao salvar os dados em Excel: {e}")



for YEAR in YEARS:
    print(f"Processando o ano {YEAR}...")
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Nº Processo","Órgão","Data de Abertura","Objeto", "Razão Social", "Total Adjudicado"])  # Adicionar cabeçalhos

    processos = []


    try:

        # Configurações do ChromeDriver
        options = Options()
        options.add_argument("--headless") # Executar em segundo plano (sem abrir o navegador) # SE QUISER VISUZALIZAR, COMENTE ESSA LINHA
        options.add_experimental_option("detach", True)  # Mantém o navegador aberto após o script terminar
        driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

        # Acessar o site
        url = "https://transparencia.pb.gov.br/relatorios/?rpt=licitacoes"
        driver.get(url)

        # Aguardar o carregamento da página
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("Página carregada.")
        except Exception as e:
            print(f"Erro ao carregar a página: {e}")

        # Fechar o pop-up de cookies (se existir)
        try:
            botao_ok = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'OK')]"))
            )
            botao_ok.click()
            print("Pop-up de cookies fechado.")
        except:
            print("Nenhum pop-up de cookies encontrado.")

        # Preencher os filtros
        try:
            select_ano = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='RPTRender_ctl08_ctl03_ddValue']"))
            )
            Select(select_ano).select_by_value(YEAR)  # Seleciona o ano 2019
            print(f'Ano de abertura selecionado: {YEAR}')
            time.sleep(1)  # Aguarda 2 segundos

            # Selecionar o mês inicial
            select_mes_inicial = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='RPTRender_ctl08_ctl07_ddValue']"))
            )

            Select(select_mes_inicial).select_by_value("1")  # Seleciona JANEIRO
            print("Mês inicial selecionado: JANEIRO")
            time.sleep(1)  # Aguarda 2 segundos

            # Selecionar o mês final
            select_mes_final = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='RPTRender_ctl08_ctl11_ddValue']"))
            )
            Select(select_mes_final).select_by_value("12")  # Seleciona DEZEMBRO
            print("Mês final selecionado: DEZEMBRO")
            time.sleep(1)  # Aguarda 2 segundos

            # Selecionar a modalidade
            select_modalidade = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='RPTRender_ctl08_ctl15_ddValue']"))
            )
            Select(select_modalidade).select_by_value("1")  # Seleciona DISPENSA DE LICITAÇÃO
            print("Modalidade selecionada: DISPENSA DE LICITAÇÃO")
            time.sleep(1)  # Aguarda 2 segundos

            # Selecionar a situação
            select_situacao = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='RPTRender_ctl08_ctl19_ddValue']"))
            )
            Select(select_situacao).select_by_value("7")  # Seleciona PROCESSO FINALIZADO DISPENSA
            print("Situação selecionada: PROCESSO FINALIZADO DISPENSA")
            time.sleep(1)  # Aguarda 2 segundos

        except Exception as e:
            print(f"Erro ao preencher os filtros: {e}")

        # Clicar no botão "Exibir Relatório"
        try:
            botao_exibir = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='RPTRender_ctl08_ctl00']"))
            )
            botao_exibir.click()
            print("Botão 'Exibir Relatório' clicado.")
        except Exception as e:
            print(f"Erro ao clicar no botão 'Exibir Relatório': {e}")



        # Aguardar o carregamento da tabela
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[3]/td[1]/div/a/div"))
            )
            print("Tabela carregada.")
            ndocs = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[1]/table/tbody/tr[23]/td[2]/div/div").text
            ndocs = float(ndocs.split(' ')[2]) #numero de documentos total encontrados para o ano
            npages = math.ceil(ndocs/20) #numero de documentos total encontrados para o ano/20 (pois sao exibidas 20 docs por pagina)
            
        except Exception as e:
            print(f"Erro ao carregar a tabela: {e}")


        # ========================================= Iterar sobre cada PAGINA =================================================================================
        count = 0
        t_drive = 30 #tempo de espera para carregar a pagina
        ninicial = 1
        # pg = 55
        # ninicial = pg-1

        # for i in range(ninicial):
        #     next_page = WebDriverWait(driver, t_drive).until(
        #     EC.element_to_be_clickable((By.XPATH, "//*[@id='RPTRender_ctl09_ctl00_Next_ctl00_ctl00']"))
        #     )
        #     ActionChains(driver).move_to_element(next_page).click().perform()
        #     print(f"Indo para a próxima página...")
        #     time.sleep(1)  
        
        for i in range(ninicial, npages+1):
            try:
                # Aguardar o carregamento da página
                
                print(f"=========================================  PÁGINA {i} de {npages} ============================================================================")
                

                WebDriverWait(driver, 50).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                
            # =========================== Iterar sobre cada PROCESSO DE CADA PÁGINA E EXTRAIR SEUS DADOS  (Iterando sobre os processos de cada página aqui) ====================
                try:
                    elementos_processos = WebDriverWait(driver, 50).until(
                        EC.presence_of_all_elements_located((By.XPATH, ".//a[contains(@data-drillthroughurl, 'Num_Processo')]"))
                    )

                    for index in range(len(elementos_processos)): 

                        elementos_processos = WebDriverWait(driver, 50).until(
                            EC.presence_of_all_elements_located((By.XPATH, ".//a[contains(@data-drillthroughurl, 'Num_Processo')]"))
                        )
                        print("\n------------------------------------------------------------------")

                        try:    
                            
                            elemento = elementos_processos[index]
                            elemento.click()

                            #aguardar o carregamento da página do processo
                            WebDriverWait(driver, t_drive).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )

                            # Aguardar o carregamento dos elementos
                            WebDriverWait(driver, t_drive).until(
                                EC.presence_of_element_located((By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[5]/td[1]/div/div"))
                            )


                            # Extrair o Nº do processo
                            if driver.find_elements(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td[5]/div/div"):
                                n_processo = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td[5]/div/div").text
                                n_processo = n_processo.split(' ')[3].split('/')[0]
                                n_processo = n_processo.split('\n')[0]
                                print(f"Processo: {n_processo}")
                            else:
                                print("Processo não encontrado")
                                orgao = 'NaN'

                            #Extrair o Órgão
                            if driver.find_elements(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[3]/td[1]/div/div"):
                                orgao = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[3]/td[1]/div/div").text
                                print(f"Órgão: {orgao}")
                            else:
                                print("Órgão não encontrado")
                                orgao = 'NaN'
                            
                            #Extrair o data de Abertura
                            if driver.find_elements(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[3]/td[4]/div/div"):
                                data = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[3]/td[4]/div/div").text
                                print(f"Data de Início: {data}")
                            else:
                                print("Data não encontrada")
                                data = 'NaN'

                            # Extrair o objeto
                            if driver.find_elements(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[5]/td[1]/div/div"):
                                objeto = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[5]/td[1]/div/div").text
                                print(f"Objeto: {objeto}")
                            else:
                                print("Objeto não encontrado.")
                                objeto = 'NaN'

                            # Extrair o total adjudicado
                            if driver.find_elements(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[5]/td[4]/div/div"):
                                total_adjudicado = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[5]/td[4]/div/div").text
                                print(f"Total Adjudicado: {total_adjudicado}")
                            else:
                                print("Total Adjudicado não encontrado.")
                                total_adjudicado = 'NaN'

                            # Extrair a razão social (Empresa ganhadora)
                            if driver.find_elements(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[3]/td[5]/div/div"):
                                razao_social = driver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/table/tbody/tr[4]/td[3]/div/div[1]/div/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td[3]/table/tbody/tr[9]/td/table/tbody/tr/td/table/tbody/tr[3]/td[5]/div/div").text
                                print(f"Razão Social: {razao_social}")
                            else:
                                print("Razão Social não encontrada.")
                                razao_social = "Razão Social não encontrada"



                            # Salvar os dados na planilha (linha por linha)
                            if n_processo and orgao and data and objeto and razao_social and total_adjudicado:
                                salvar_dados_excel([n_processo, orgao, data, objeto, razao_social, total_adjudicado], sheet)

                            try:
                                workbook.save(f"dados_processos_{YEAR}.xlsx")  # Salva o arquivo com o ano no nome
                                print(f"Planilha final salva como 'dados_processos_{YEAR}.xlsx'.")
                            except Exception as e:
                                print(f"Erro ao salvar a planilha para o ano {YEAR}: {e}")

                            time.sleep(1)
                            botao_retorno = driver.find_element(By.XPATH, "//*[@id='RPTRender_ctl09_ctl01_ctl00_ctl00_ctl00']")  # Localize o botão de retorno
                            ActionChains(driver).move_to_element(botao_retorno).click().perform()

                            # Espera a página voltar e carregue o próximo processo
                            time.sleep(5)  # Adapte conforme o tempo de resposta da página

                            WebDriverWait(driver, 50).until(
                            EC.presence_of_all_elements_located((By.XPATH, ".//a[contains(@data-drillthroughurl, 'Num_Processo')]"))
                            )

                            count += 1
                            print(f"\nProcesso {count} de {ndocs} processos processados.")

                        except Exception as e:
                            print(f"Erro ao clicar no processo {index}: {e}")



                except Exception as e:
                    print(f"Erro ao clicar no número do processo: {e}")

                #PROSSEGUINDO PARA A PRÓXIMA PÁGINA
                next_page = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='RPTRender_ctl09_ctl00_Next_ctl00_ctl00']"))
                )
                ActionChains(driver).move_to_element(next_page).click().perform()
                print(f"Indo para a próxima página...")
                time.sleep(1)  

            except Exception as e:
                print(f"Erro ao carregar a página: {e}")

            finally:
                # Fechar a janela atual e reabrir o navegador para o próximo processo
                print("Navegador reiniciado para o próximo processo.")

    except Exception as e:
        # print(f"Erro ao processar o processo {i - 2}: {e}")
        print("Processo ok...")

    # Manter o navegador aberto para inspeção
    print(f"Processo {count} de {ndocs} processos processados.")
    print("Script concluído. O navegador permanecerá aberto.")
    time.sleep(1)   # Mantém o navegador aberto por 10 segundos após o término do script
driver.quit()


end_time = time.time()  # Fim da contagem
elapsed_time = end_time - start_time

print(f"Tempo de execução: {elapsed_time:.4f} segundos")