# BTP Algeria - Système de Gestion Intégré

Plateforme de gestion complète pour entreprise de BTP en Algérie, conforme au SCF et aux lois sociales locales.

## 🚀 Installation Locale (Développement)

1. **Cloner le repository**
   ```bash
   git clone https://github.com/btp-algeria/btp-app.git
   cd btp-app
   ```

2. **Environnement Virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate sur Windows
   pip install -r requirements.txt
   ```

3. **Configuration**
   Copier `.env.example` vers `.env` et configurer les variables (Database, Redis, Encryption Key).

4. **Infrastructure Docker**
   ```bash
   docker-compose up -d  # Lance PostgreSQL et Redis
   ```

5. **Initialisation Django**
   ```bash
   python manage.py migrate
   python manage.py load_initial_data  # Wilayas, SCF, Rôles, Admin
   python manage.py create_demo_data   # Données réalistes pour démo
   ```

6. **Lancement**
   ```bash
   python manage.py runserver
   ```

## 👥 Comptes de Démonstration (Mot de passe : Admin@2025!)
- **Administrateur** : `admin`
- **Directeur Général** : `dg_benali`
- **RH** : `rh_kamel`
- **Comptable** : `comptable_amina`

## 🏗️ Structure des Modules
- **accounts** : Authentification forte, RBAC, 2FA.
- **employees** : Dossier personnel, Paie (IRG/CNAS), Congés.
- **projects** : Suivi chantiers, Situations de travaux, Rentabilité.
- **suppliers** : Achats, Devis, Stock matériaux, Facturation.
- **finance** : Plan comptable SCF, Trésorerie, Fiscalité (TAP/IBS).
- **fleet** : Maintenance engins, Carburant, Alertes CT/Assurance.
- **audit** : Logs immuables de toutes les actions sensibles.

## 🛡️ Sécurité
Consultez le fichier [SECURITY_CHECKLIST.md](SECURITY_CHECKLIST.md) pour les détails sur le durcissement du système.

## 📧 Support
Contactez l'équipe technique à `support@btpalgeria.dz`.
