from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from views.dashboard import (
    auth_views,
    user_views,
    role_views,
    language_views,
    text_key_views,
    genre_views,
    gem_views,
    novel_views,
    author_views,
    payment_method_views,
    slider_views,
)
from views.website import page_views as website_page_views
from views.website import auth_views as website_auth_views
from views.dashboard import page_views as dashboard_page_views

handler500 = dashboard_page_views.internal_server_error
urlpatterns = (
    [
        path(settings.ADMIN_LOGIN_URL, admin.site.urls),


# // Dashboard URLs -----------------------------------------------------------------------------------------------------
        path("dashboard/", dashboard_page_views.dashboard, name="dashboard"),
        path("under-maintenance/",dashboard_page_views.under_maintenance,name="under_maintenance",),
        path(settings.DASHBOARD_LOGIN_URL,auth_views.dashboard_login,name="dashboard_login",),
        path(settings.DASHBOARD_LOGOUT_URL,auth_views.dashboard_logout,name="dashboard_logout",),
        path("dashboard/profile/", auth_views.profile, name="dashboard_profile"),
        path("dashboard/site-settings/",dashboard_page_views.site_settings,name="site_settings",),
        path("accounts/", include("allauth.urls")),


# // UserModel ----------------------------------------------------------------------------------------------------
        path("dashboard/user/list/", user_views.user_list, name="user_list"),
        path("dashboard/user/create/", user_views.user_create, name="user_create"),
        path("dashboard/user/update/<uuid:pk>/",user_views.user_update,name="user_update",),
        path("dashboard/user/delete/<uuid:pk>/",user_views.user_delete,name="user_delete",),
        path("dashboard/user/export/excel/",user_views.user_export_excel,name="user_export_excel",),
        path("dashboard/user/export/pdf/",user_views.user_export_pdf,name="user_export_pdf",),


# // RoleModel ----------------------------------------------------------------------------------------------------
        path("dashboard/role/list/", role_views.role_list, name="role_list"),
        path("dashboard/role/create/", role_views.role_create, name="role_create"),
        path("dashboard/role/update/<uuid:pk>/", role_views.role_update, name="role_update",),
        path("dashboard/role/delete/<uuid:pk>/",role_views.role_delete,name="role_delete",),
        path("dashboard/role/export/excel/",role_views.role_export_excel,name="role_export_excel",),
        path("dashboard/role/export/pdf/",role_views.role_export_pdf,name="role_export_pdf",),


# // LanguageModel ----------------------------------------------------------------------------------------------------
        path("dashboard/language/list/",language_views.language_list,name="language_list",),
        path("set-language/", language_views.set_language, name="set_language"),
        path("dashboard/language/create/",language_views.language_create,name="language_create",),
        path("dashboard/language/update/<uuid:pk>/",language_views.language_update,name="language_update",),
        path("dashboard/language/delete/<uuid:pk>/",language_views.language_delete,name="language_delete",),


# // TextKeyModel ----------------------------------------------------------------------------------------------------
        path("dashboard/text-key/list/",text_key_views.text_key_list,name="text_key_list",),
        path("dashboard/text-key/create/",text_key_views.text_key_create,name="text_key_create",),
        path("dashboard/text-key/update/<uuid:pk>/",text_key_views.text_key_update,name="text_key_update",),
        path("dashboard/text-key/delete/<uuid:pk>/",text_key_views.text_key_delete,name="text_key_delete",),
        path("dashboard/translations/save/",text_key_views.save_translation,name="save_translation",),


# // GenreModel -----------------------------------------------------------------------------------------------------------
        path("dashboard/genre/list/", genre_views.genre_list, name="genre_list"),
        path("dashboard/genre/create/", genre_views.genre_create, name="genre_create"),
        path("dashboard/genre/update/<uuid:pk>/", genre_views.genre_update, name="genre_update"),
        path("dashboard/genre/delete/<uuid:pk>/", genre_views.genre_delete, name="genre_delete"),


# // GemModel --------------------------------------------------------------------------------------------------------------
        path("dashboard/gem/list/", gem_views.gem_list, name="gem_list"),
        path("dashboard/gem/create/", gem_views.gem_create, name="gem_create"),
        path("dashboard/gem/update/<uuid:pk>/", gem_views.gem_update, name="gem_update"),
        path("dashboard/gem/delete/<uuid:pk>/", gem_views.gem_delete, name="gem_delete"),
        path("dashboard/gem/order/list/", gem_views.gem_order_list, name="gem_order_list"),
        path("dashboard/gem/order/approve/<uuid:pk>/", gem_views.gem_order_approve, name="gem_order_approve"),
        path("dashboard/gem/order/reject/<uuid:pk>/", gem_views.gem_order_reject, name="gem_order_reject"),


# // AuthorModel ------------------------------------------------------------------------------------------------------------
        path("dashboard/author/list/", author_views.author_list, name="author_list"),
        path("dashboard/author/create/", author_views.author_create, name="author_create"),
        path("dashboard/author/update/<uuid:pk>/", author_views.author_update, name="author_update"),
        path("dashboard/author/delete/<uuid:pk>/", author_views.author_delete, name="author_delete"),
        path("dashboard/author/salary/list/", author_views.author_salary_list, name="author_salary_list"),
        path("dashboard/author/salary/paid/<uuid:pk>/", author_views.author_salary_mark_paid, name="author_salary_mark_paid"),


# // NovelModel -------------------------------------------------------------------------------------------------------------
        path("dashboard/novel/list/",novel_views.novel_list,name="novel_list",),
        path("dashboard/novel/create/",novel_views.novel_form,name="novel_create",),
        path("dashboard/novel/update/<uuid:pk>/",novel_views.novel_form,name="novel_update",),
        path("dashboard/novel/delete/<uuid:pk>/",novel_views.novel_delete,name="novel_delete",),
        path("dashboard/novel/sales/", novel_views.novel_sales_list, name="novel_sales_list"),
        path("dashboard/novel-chapter/create/<uuid:novel_id>/",novel_views.novel_chapter_create,name="novel_chapter_create",),
        path("dashboard/novel-chapter/update/<uuid:pk>/",novel_views.novel_chapter_update,name="novel_chapter_update",),
        path("dashboard/novel-chapter/delete/<uuid:pk>/",novel_views.novel_chapter_delete,name="novel_chapter_delete",),


# // PaymentMethodModel -----------------------------------------------------------------------------------------------------
        path("dashboard/payment/method/list/", payment_method_views.payment_method_list, name="payment_method_list"),
        path("dashboard/payment/method/create/", payment_method_views.payment_method_create, name="payment_method_create"),
        path("dashboard/payment/method/update/<uuid:pk>/", payment_method_views.payment_method_update, name="payment_method_update"),
        path("dashboard/payment/method/delete/<uuid:pk>/", payment_method_views.payment_method_delete, name="payment_method_delete"),


# // SliderModel -----------------------------------------------------------------------------------------------------------
        path('sliders/',slider_views.slider_list, name="slider_list"),
        path('sliders/create/',slider_views.slider_create, name="slider_create"),
        path('sliders/update/<uuid:pk>/',slider_views.slider_update, name="slider_update"),
        path('sliders/delete/<uuid:pk>/',slider_views.slider_delete, name="slider_delete"),
        path('sliders/activate/<uuid:pk>/',slider_views.slider_activate, name="slider_activate"),
        path('sliders/deactivate/<uuid:pk>/',slider_views.slider_deactivate, name="slider_deactivate"),


# // LockScreen ----------------------------------------------------------------------------------------------------------
        path("lock-screen/", dashboard_page_views.lock_screen, name="lock_screen"),
        path("unlock/", dashboard_page_views.unlock, name="unlock"),
        path("locked/", dashboard_page_views.locked, name="locked"),


# // PWA --------------------------------------------------------------------------------------------------------------------
        path("", include("pwa.urls")),
        path("", website_page_views.index, name="home"),
        path("novel/detail/<uuid:id>/", website_page_views.novel_detail, name="novel_detail"),
        path("novel/chapter/<uuid:id>/", website_page_views.chapter_detail, name="chapter_detail"),
        path("novel/chapter/buy/<uuid:id>/", website_page_views.buy_chapter, name="buy_chapter"),
        path("novel/bookmark/<uuid:id>/", website_page_views.bookmark, name="bookmark"),
        path("author/<uuid:id>/", website_page_views.author_profile, name="author_profile"),
        path("author/<uuid:id>/follow/", website_page_views.follow_author, name="follow_author"),
        path("checkout/<uuid:id>/", website_page_views.checkout, name="checkout"),
        path("gem", website_page_views.gem, name="gem"),
        path("website/profile/", website_page_views.profile, name="website_profile"),
        path("login/", website_auth_views.login_view, name="website_login"),
        path("logout/", website_auth_views.logout_view, name="website_logout"),
        path("register/", website_auth_views.register_view, name="website_register"),
        path("verify-email/<uidb64>/<token>/",website_auth_views.verify_email,name="verify_email",),
        path("forgot-password/",website_auth_views.forgot_password,name="forgot_password",),
        path("reset-password/<uidb64>/<token>/",website_auth_views.reset_password,name="reset_password",),


# // Page Not Found -----------------------------------------------------------
        re_path(r"^.*/$", dashboard_page_views.page_not_found),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
