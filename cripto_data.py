from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import requests
import sqlite3

API_KEY = 'df843973-69dc-4af0-88b6-ab79ea9cef66'
URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

# criptos a consultar
criptos_to_insert = ['BTC', 'ETH', 'SOL']

parameters = {
    'symbol': ','.join(criptos_to_insert),
    'convert': 'USD'
}

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': API_KEY,
}

# obtener el json con los datos de la api
def get_cripto_data():
    response = requests.get(URL, headers=headers, params=parameters)
    try:
      data = response.json()
      return data
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e)

# create de la base y tabla
def create_database():
    connection = sqlite3.connect('criptos.db')
    cursor = connection.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS criptomonedas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        precio INTEGER,
                        volumen INTEGER,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    
    connection.commit()
    return connection

# insert de los datos
def insert_data(connection, name, price, volume):
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO criptomonedas (nombre, precio, volumen) VALUES (?, ?, ?)''', (name, price, volume))
    connection.commit()

def main():
    cripto_data = get_cripto_data()
    #print(cripto_data)
    if cripto_data:
        connection = create_database()
        
        for cripto in criptos_to_insert:
            try:                
                name = cripto_data['data'][cripto]['name']
                price = int(cripto_data['data'][cripto]['quote']['USD']['price'])
                volume = int(cripto_data['data'][cripto]['quote']['USD']['volume_24h'])
                
                insert_data(connection, name, price, volume)
                
                print(f"Datos insertados para {name}: Precio={price}, Volumen={volume}")
            except KeyError:
                print(f"Error al procesar los datos para {cripto}")
        
        connection.close()
    else:
        print("No se pudieron obtener datos de la API.")

if __name__ == '__main__':
    main()

#para hacer el cron que ejecute todos los dias a las 8am: 
# crontab -e
# 0 8 * * * /ruta/a/tu_script.py
