def menu_processor(request):
    if not request.user.is_authenticated:
        return {'menu_items': []}
    
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin = request.user.is_superuser or 'admin' in user_groups
    
    menu = [
        {'name': 'Tableau de Bord', 'url': 'dashboard_router', 'icon': 'fas fa-tachometer-alt'},
    ]
    
    if is_admin or 'rh' in user_groups:
        menu.append({'name': 'Ressources Humaines', 'url': 'employee_list', 'icon': 'fas fa-users'})
        
    if is_admin or 'chef_projet' in user_groups or 'dg' in user_groups:
        menu.append({'name': 'Projets', 'url': 'projet_list', 'icon': 'fas fa-project-diagram'})
        
    if is_admin or 'achats' in user_groups or 'dg' in user_groups:
        menu.append({'name': 'Achats & Fournisseurs', 'url': 'fournisseur_list', 'icon': 'fas fa-shopping-cart'})
        
    if is_admin or 'comptable' in user_groups or 'dg' in user_groups:
        menu.append({'name': 'Finance', 'url': 'finance_dashboard', 'icon': 'fas fa-file-invoice-dollar'})
        
    if is_admin or 'parc' in user_groups or 'chef_projet' in user_groups:
        menu.append({'name': 'Parc Engins', 'url': 'engin_list', 'icon': 'fas fa-truck-pickup'})
        
    if is_admin:
        menu.append({'name': 'Sécurité & Audit', 'url': 'audit_logs', 'icon': 'fas fa-shield-alt'})
        menu.append({'name': 'Administration', 'url': 'user_management', 'icon': 'fas fa-cogs'})
        
    return {
        'menu_items': menu,
        'notifications_count': 3,
        'alertes_systeme': [
            {'message': 'Contrat CDD expirant (K. Benali)', 'date': '2026-05-15', 'niveau': 'critique'},
            {'message': 'Retard livraison COSIDER', 'date': '2026-05-02', 'niveau': 'avertissement'},
            {'message': 'Maintenance préventive Camion #001', 'date': '2026-05-01', 'niveau': 'info'},
        ],
        'is_2fa_enabled': getattr(request.user, 'profile', None).two_fa_enabled if hasattr(request.user, 'profile') else False
    }
