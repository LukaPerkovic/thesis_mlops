# MLOps FinOps Projekat

**Autor:** Luka Perković


Ovaj repozitorijum demonstrira kompletan MLOps tok rada za projekat mašinskog učenja, dizajniran kao deo master rada. Cilj je da se prikažu moderne MLOps prakse koristeći otvoreni kod i slobodne cloud resurse gde god je to moguće.

## Pregled Projekta

Projekat implementira *pipeline* mašinskog učenja od početka do kraja za problem klasifikacije (npr. otkrivanje prevara). Pokriva sve glavne faze mašinskog učenja:

- **Ekstraktovanje & Procesuiranje podataka:** Učitavanja podataka iz lokalnih fajlova ili AWS S3, procesuiranje ili priprema podataka za treniranje i predikciju.
- **Treniranje modela & Optimizacija:** Treniranje modela sa podešavanjem hiperparametara i evaluacijom postignuća.
- **Registar Modela & Deployment:** Registracija modela sa MLflow-om (kompatibilan sa Databricksom), upravljanje verzijama modela i deployment modela sa endpointovima.
- **Pipeline Predikcije:** Batch predikcija na novim podacima i eksportovanje, sa integrisanim klaud endpointovima.
- **Infrastructure as Code:** Upravljanje klaud resursima (npr., S3 baketi, IAM uloge) korišćenjem Terraforma.
- **CI/CD:** Automatsko testiranje i deployment korišćenjem GitHub Actions servisa.


## Tokovi

### 1. Trening pipeline


- Učitava i prethodno obrađuje podatke iz S3 ili lokalnih datoteka.
- Trenira i podešava XGBoost klasifikator.
- Procenjuje performanse modela.
- Registruje modele spremne za produkciju u MLflow-u.
- Pokreće se putem GitHub akcija (`cd.yaml`).

### 2. Deployment Pipeline

- Deplojuje poslednji "šampion model" na Databriksov endpoint.
- Upravlja se putem MLflowa i Databriksovog API-ja.

### 3. Predikcija Pipeline

- Učitava nove podatke za inferenciju.
- Šalje podatke na endpoint lansiranog modela.
- Čuva predikcije u S3 ili na lokalu.
- Pokreće se putem GitHub akcija (`inference.yaml`).

### 4. Infrastructure as Code

- AWS S3 baketi za skladištenje podataka (dev/prod).
- IAM uloge i polise za kontrolu bezbednosti.
- Upravlja se putem Terraformovih skripti `src/iac/`.

## CI/CD

- CI: Pokreće testove i provere formatiranja koda pri svakoj akciji push ili merge na granu `main`.
- CD: Automatski trenira i lansira modele po rasporedu ili po potrebi.

## Fokus na Free Tier & Open Source servisima

- Sve komponente su odabrane tako da minimiziraju troškove.
- AWS Free tier je korišćen za S3.
- MLflow je open-source i korišćen za registraciju modela i serviranje predikcija u okviru Databriksove besplatne edicije.
- Sav kod je open-source i može se reproducirati, ako i samo ako korisnik produkuje svoje kredencijale.
