import os
import time
import shutil
import pandas as pd
import mysql.connector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Criar diretório para planilhas se não existir
if not os.path.isdir("planilhas"):
    os.mkdir("./planilhas")

download_dir = os.path.join(os.getcwd(), "planilhas")

def getSheet(uf):
    file_uf = os.path.join(download_dir, f"Lista_imoveis_{uf}.csv")
    if not os.path.exists(file_uf):
        print(f'Baixando planilha para {uf}')
        chrome_options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": download_dir, "directory_upgrade": True}
        chrome_options.add_experimental_option("prefs", prefs)
        
        browser = webdriver.Chrome(options=chrome_options)
        browser.get('https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp')
        
        dropdown = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "cmb_estado")))
        select = Select(dropdown)
        select.select_by_visible_text(uf)
        
        download_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "btn_next1")))
        download_button.click()
        
        time.sleep(5)  # Aguarda o download
        browser.quit()

def mergeSheets():
    print("Unificando planilhas")
    
    ufs = ['PR', 'MG', 'SP', 'GO', 'RJ']
    df_list = []
    
    for uf in ufs:
        file_path = os.path.join(download_dir, f"Lista_imoveis_{uf}.csv")
        if os.path.exists(file_path):
            df_list.append(pd.read_csv(file_path, sep=';', skiprows=2, encoding='latin-1', on_bad_lines='skip'))
    
    if df_list:
        df_merged = pd.concat(df_list, ignore_index=True)
        df_merged.columns = ['numero_imovel', 'uf', 'cidade', 'bairro', 'endereco', 'preco', 'valor_avaliacao', 'desconto', 'descricao', 'modalidade_da_venda', 'link_de_acesso']
        df_merged.to_csv(os.path.join(download_dir, 'Lista_imoveis.csv'), index=False, sep=',')

def getDatabase():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )
    if conn.is_connected():
        print("Conectado ao banco de dados")
    return conn

def getProperty(conn, codProperty):
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM imoveis2 WHERE numero_imovel = {codProperty};"
    cursor.execute(query)
    return cursor.fetchall()

def saveData(conn):
    csv_insert = os.path.join(download_dir, "Lista_imoveis_a_inserir.csv")
    if os.path.exists(csv_insert):
        cursor = conn.cursor()
        df = pd.read_csv(csv_insert, skiprows=1)
        
        for _, row in df.iterrows():
            cod_imovel = row.iloc[0]
            if not getProperty(conn, cod_imovel):
                columns = 'numero_imovel, uf, cidade, bairro, endereco, preco, valor_avaliacao, desconto, descricao, modalidade_da_venda, link_de_acesso'
                values = ', '.join(['%s'] * len(row))
                sql = f"INSERT INTO imoveis2 ({columns}) VALUES ({values})"
                cursor.execute(sql, tuple(row))    
                conn.commit()
                print(f"Imóvel {cod_imovel} inserido com sucesso!")

def hasInSheets(df, cod_imovel):
    return cod_imovel not in df["numero_imovel"].values

def removeData(conn):
    csv_file = os.path.join(download_dir, "Lista_imoveis.csv")
    if not os.path.exists(csv_file):
        print("Arquivo de imóveis não encontrado.")
        return
    
    df = pd.read_csv(csv_file, encoding='latin-1')
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT numero_imovel FROM imoveis2 WHERE numero_imovel IS NOT NULL")
    
    ids_to_remove = [str(prop["numero_imovel"]) for prop in cursor.fetchall() if hasInSheets(df, prop["numero_imovel"])]
    
    if ids_to_remove:
        cursor.execute(f"DELETE FROM imoveis2 WHERE numero_imovel IN ({', '.join(ids_to_remove)});")
        conn.commit()
        print(f"Removidos {len(ids_to_remove)} imóveis.")

def main():
    ufs = ['PR', 'MG', 'SP', 'GO', 'RJ']
    csv_file = os.path.join(download_dir, "Lista_imoveis.csv")
    
    for uf in ufs:
        getSheet(uf)
    
    if not os.path.exists(csv_file):
        mergeSheets()
    
    conn = getDatabase()
    removeData(conn)
    saveData(conn)
    
    shutil.rmtree(download_dir)
    print("Processo concluído!")

if __name__ == "__main__":
    main()
