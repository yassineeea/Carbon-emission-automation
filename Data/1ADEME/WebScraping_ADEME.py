import requests

def download_csv():

    url = "https://data.ademe.fr/data-fair/api/v1/datasets/base-carboner/full"
    response = requests.get(url)

    if response.status_code == 200:
        with open("ADEME_input1.csv", "wb") as f:
            f.write(response.content)
        print(f"Fichier téléchargé et enregistré !")
    else:
        raise Exception(f"Erreur lors du téléchargement : {response.status_code}")

download_csv()
