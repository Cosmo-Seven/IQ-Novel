def sidebar(request):
    return {
        "SIDEBAR_MENU": [
            {
                "title": "dashboard",
                "permissions": ["is_staff"],
                "items": [
                    {
                        "label": "dashboard",
                        "url_name": "dashboard",
                        "icon": "ti ti-dashboard",
                    },
                    {
                        "label": "event",
                        "url_name": "reward_list",
                        "icon": "ti ti-calendar-event",
                        "permission": "view_rewardmodel",
                    },
                ],
            },
            {
                "title": "Slider",
                "permissions": ["view_slidermodel"],
                "items": [
                    {
                        "label": "slider",
                        "url_name": "slider_list",
                        "icon": "ti ti-photo",
                        "permission": "view_slidermodel",
                    },
                ]
            },
            {
                "title": "Gem",
                "permissions": ["view_gemmodel"],
                "items": [
                    {
                        "label": "gems",
                        "url_name": "gem_list",
                        "icon": "ti ti-diamond",
                        "permission": "view_gemmodle",
                    },
                    {
                        "label": "gem_orders",
                        "url_name": "gem_order_list",
                        "icon": "ti ti-list-check",
                        "permission": "view_gemordermodel",
                    },
                ]
            },
            {
                "title": "Novel",
                "permissions": [
                    "view_genremodel",
                    "view_novelmodel",
                    "view_authormodel",
                    "view_authorsalarymodel",
                ],
                "items": [
                    {
                        "label": "genre",
                        "url_name": "genre_list",
                        "icon": "ti ti-category",
                        "permission": "view_genremodel",
                    },
                    {
                        "label": "authors",
                        "url_name": "author_list",
                        "icon": "ti ti-user-edit",
                        "permission": "view_authormodel",
                    },
                    {
                        "label": "author_salaries",
                        "url_name": "author_salary_list",
                        "icon": "ti ti-report-money",
                        "permission": "view_authorsalarymodel",
                    },
                    {
                        "label": "novel",
                        "url_name": "novel_list",
                        "icon": "ti ti-book",
                        "permission": "view_novelmodel",
                    },
                    {
                        "label": "novel_sales",
                        "url_name": "novel_sales_list",
                        "icon": "ti ti-chart-bar",
                        "permission": "view_novelmodel",
                    },
                ]
            },
            {
                "title": "Payment",
                "permissions": ["view_paymentmethodmodel"],
                "items":[
                    {
                        "label": "payment_method",
                        "url_name": "payment_method_list",
                        "icon": "ti ti-credit-card",
                        "permission": "view_paymentmethodmodel",
                    },
                ]
            },
            {
                "title": "user_administration",
                "permissions": [
                    "view_usermodel",
                    "view_rolemodel",
                ],
                "items": [
                    {
                        "label": "users",
                        "url_name": "user_list",
                        "icon": "ti ti-users",
                    },
                    {
                        "label": "roles_and_permissions",
                        "url_name": "role_list",
                        "icon": "ti ti-shield-lock",
                    },
                ],
            },
            {
                "title": "system_settings",
                "permissions": [
                    "view_sitemodel",
                    "view_languagemodel",
                    "view_textkeymodel",
                ],
                "items": [
                    {
                        "label": "company_settings",
                        "url_name": "site_settings",
                        "icon": "ti ti-building",
                    },
                    {
                        "label": "language_settings",
                        "url_name": "language_list",
                        "icon": "ti ti-language",
                    },
                    {
                        "label": "translation_keys",
                        "url_name": "text_key_list",
                        "icon": "ti ti-message-language",
                    },
                ],
            },
        ]
    }