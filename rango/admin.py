from django.contrib import admin
from django.contrib.auth.models import User

from .models import Category, Page, UserProfile


class PageInline(admin.TabularInline):
    model = Page
    extra = 3


class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Profile Infos", {'fields': ['website', 'picture', ]}),
    ]
    list_display = ('get_username', 'get_email', 'website', 'picture')
    search_fields = ['get_username', 'get_email']


class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Primary Infos", {'fields': ['name', 'slug', ]}),
        ("Statistics", {'fields': ['views', 'likes', ]}),
    ]
    inlines = [PageInline, ]
    list_display = ('name', 'views', 'likes', 'pages_count')
    search_fields = ['name']
    prepopulated_fields = {"slug": ("name",)}


class PageAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Primary Infos", {'fields': ['title', 'url', ]}),
        ("Statistics", {'fields': ['views', ]}),
        ("Category", {'fields': ['category', ]})
    ]
    list_display = ('title', 'url', 'views', 'category')
    list_filter = ['category']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
