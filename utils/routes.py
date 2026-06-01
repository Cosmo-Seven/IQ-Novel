from django.urls import reverse_lazy


def routes(request):
    return {
        # ======================================== Auth ========================================
        "dashboard_login_url": reverse_lazy("dashboard_login"),
        "dashboard_logout_url": reverse_lazy("dashboard_logout"),
        "dashboard_profile_url": reverse_lazy("dashboard_profile"),
        "admin_url": reverse_lazy("admin"),
        "site_settings_url": reverse_lazy("site_settings"),
        "lock_screen_url": reverse_lazy("lock_screen"),
        "locked_url": reverse_lazy("locked"),
        "unlock_url": reverse_lazy("unlock"),
        "under_maintenance_url": reverse_lazy("under_maintenance"),
        # ======================================== Dashboard ========================================
        "dashboard_url": reverse_lazy("dashboard"),
        # ======================================== UserModel ========================================
        "user_list_url": reverse_lazy("user_list"),
        "user_create_url": reverse_lazy("user_create"),
        "user_export_excel_url": reverse_lazy("user_export_excel"),
        "user_export_pdf_url": reverse_lazy("user_export_pdf"),
        # ======================================== LanguageModel ========================================
        "language_list_url": reverse_lazy("language_list"),
        "language_create_url": reverse_lazy("language_create"),
        # ======================================== TextKeyModel ========================================
        "text_key_list_url": reverse_lazy("text_key_list"),
        "text_key_create_url": reverse_lazy("text_key_create"),
        # ======================================== RoleModel ========================================
        "role_list_url": reverse_lazy("role_list"),
        "role_create_url": reverse_lazy("role_create"),
        "role_export_excel_url": reverse_lazy("role_export_excel"),
        "role_export_pdf_url": reverse_lazy("role_export_pdf"),
        # ======================================== GenreModel ========================================
        "genre_list_url": reverse_lazy("genre_list"),
        "genre_create_url": reverse_lazy("genre_create"),
        # ======================================== GemModel ========================================
        "gem_list_url": reverse_lazy("gem_list"),
        "gem_create_url": reverse_lazy("gem_create"),
        "gem_order_list_url": reverse_lazy("gem_order_list"),
        # ======================================== AuthorModel ========================================
        "author_list_url": reverse_lazy("author_list"),
        "author_create_url": reverse_lazy("author_create"),
        "author_salary_list_url": reverse_lazy("author_salary_list"),
        # ======================================== NovelModel ========================================
        "novel_list_url": reverse_lazy("novel_list"),
        "novel_create_url": reverse_lazy("novel_create"),
        "novel_sales_list_url": reverse_lazy("novel_sales_list"),
        # ======================================== PaymentMethodModel ========================================
        "payment_method_list_url": reverse_lazy("payment_method_list"),
        "payment_method_create_url": reverse_lazy("payment_method_create"),
        # ======================================== SliderModel ========================================
        "slider_list_url": reverse_lazy("slider_list"),
        "slider_create_url": reverse_lazy("slider_create"),
        # ======================================== Website ========================================
        "home_url": reverse_lazy("home"),
        "gem_url": reverse_lazy("gem"),
        
        "website_profile_url": reverse_lazy("website_profile"),
        "website_login_url": reverse_lazy("website_login"),
        "logout_url": reverse_lazy("logout"),
        "register_url": reverse_lazy("register"),
    }
