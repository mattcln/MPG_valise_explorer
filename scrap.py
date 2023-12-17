import requests
from bs4 import BeautifulSoup

url = "https://mpg.football/"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Utilisez les méthodes de BeautifulSoup pour extraire les données
    # Exemple : récupérer tous les liens sur la page
    links = soup.find_all("a")
    for link in links:
        print(link.get("href"))
else:
    print("Échec de la requête HTTP:", response.status_code)
