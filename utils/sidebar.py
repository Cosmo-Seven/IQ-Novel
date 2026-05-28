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
                        "icon": "ti ti-layout-grid",
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
                        "icon": "ti ti-layout-grid",
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
                        "icon": "ti ti-layout-grid",
                        "permission": "view_gemmodle",
                    },
                ]
            },
            {
                "title": "Novel",
                "permissions": [
                    "view_genremodel",
                    "view_novelmodel",
                ],
                "items": [
                    {
                        "label": "genre",
                        "url_name": "genre_list",
                        "icon": "ti ti-layout-grid",
                        "permission": "view_genremodel",
                    },
                    {
                        "label": "novel",
                        "url_name": "novel_list",
                        "icon": "ti ti-layout-grid",
                        "permission": "view_novelmodel",
                    }
                ]
            },
            {
                "title": "Payment",
                "permissions": ["view_paymentmethodmodel"],
                "items":[
                    {
                        "label": "payment_method",
                        "url_name": "payment_method_list",
                        "icon": "ti ti-layout-grid",
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
                        "permission": "view_usermodel",
                    },
                    {
                        "label": "roles_and_permissions",
                        "url_name": "role_list",
                        "icon": "ti ti-shield-lock",
                        "permission": "view_rolemodel",
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
                        "permission": "view_sitemodel",
                    },
                    {
                        "label": "language_settings",
                        "url_name": "language_list",
                        "icon": "ti ti-language",
                        "permission": "view_languagemodel",
                    },
                    {
                        "label": "translation_keys",
                        "url_name": "text_key_list",
                        "icon": "ti ti-message-language",
                        "permission": "view_textkeymodel",
                    },
                ],
            },
        ]
    }
