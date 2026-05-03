# SECURITY_CHECKLIST - BTP Algeria

## Contrôles d'Accès
- [x] Toutes les vues ont `@login_required` ou `LoginRequiredMixin`.
- [x] Toutes les vues sensibles ont `@role_required` (RH, Finance, etc.).
- [x] RBAC testé (test_auth.py) : un technicien ne peut pas voir la RH.
- [x] 2FA activé pour les rôles critiques (Admin, DG, Comptable).
- [x] Sessions expirantes configurées à 30 minutes d'inactivité.

## Protection des Données
- [x] Aucun secret (clé API, mots de passe) dans le code source (utilisation de `.env`).
- [x] Champs sensibles (NSS, RIB, RC, NIF) chiffrés en base de données (AES-256).
- [x] Soft delete implémenté partout (pas de suppression physique directe).
- [x] AuditLog immuable et non supprimable (vérifié par tests).
- [x] Backups PostgreSQL chiffrés et testés.

## Sécurité Réseau & Serveur
- [x] `DEBUG = False` en production.
- [x] HTTPS forcé via redirection Nginx et `SECURE_SSL_REDIRECT`.
- [x] HSTS activé (1 an) avec inclusion des sous-domaines.
- [x] Headers de sécurité (X-Frame-Options, CSP, No-Sniff) configurés.
- [x] Rate limiting (10 req/s) configuré sur Nginx.
- [x] Utilisation de `Argon2` pour le hachage des mots de passe.

## Développement & Qualité
- [x] Protection CSRF active sur tous les formulaires.
- [x] Pas de SQL brut (utilisation exclusive de l'ORM Django).
- [x] Validation côté serveur sur 100% des formulaires.
- [x] Logs rotatifs configurés pour ne pas saturer le disque.
