from django.urls import path
from django.conf.urls import url

from django.contrib.auth.views import PasswordResetView 
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordChangeView

from .views import Home
from .views import LoginView, LogoutView
from .views import Profile, Role

from .views import Users
from .views import ajax_delete_user, ajax_add_user, ajax_reset_user, ajax_reset_user1, ajax_update_user

from .views import Suppliers, SupplierAdd, SupplierUpdate, SupplierDetail, SupplierContactAdd, SubProducts
from .views import ajax_list_contacts, ajax_grid_contacts, ajax_delete_contacts, ajax_import_contacts, ajax_export_contacts
from .views import SuppliersFavorite, ajax_add_contact_favorite, ajax_delete_contact_favorite

from .views import Leads, LeadAdd, LeadUpdate, LeadDetail, LeadContactAdd
from .views import ajax_list_leads, ajax_grid_leads, ajax_delete_leads, ajax_import_leads, ajax_export_leads, ajax_export_clients
from .views import ajax_list_client_leads, ajax_grid_client_leads
from .views import LeadsFavorite, ajax_add_lead_favorite, ajax_delete_lead_favorite
from .views import ajax_send_lead_emails
from .views import ajax_transform_client_lead

from .views import ajax_add_lead_address, ajax_get_lead_address, ajax_delete_lead_address

from .views import Stocks, StocksFavorite, StockAdd, StockUpdate, StockTemp, StockUpTemp
from .views import ajax_import_stocks, ajax_delete_stocks, ajax_list_stocks, ajax_grid_stocks, ajax_export_stocks
from .views import ajax_add_favorite_stocks, ajax_delete_stock_favorite

from .views import Categories, ajax_add_category, ajax_delete_category, ajax_add_provider
from .views import WallsType, ajax_add_wallstype, ajax_delete_wallstype
from .views import Castors, ajax_add_castor, ajax_delete_castor
from .views import Colors, ajax_add_color, ajax_delete_color
from .views import Drawers, ajax_add_drawer, ajax_delete_drawer
from .views import Strips, ajax_add_strip, ajax_delete_strip
from .views import Locations, ajax_add_location, ajax_delete_location
from .views import Locks, ajax_add_lock, ajax_delete_lock
from .views import Tasks, ajax_add_task, ajax_delete_task

from .views import Groups, GroupAdd, GroupUpdate, GroupDetail, GroupsFavorite
from .views import ajax_list_groups, ajax_grid_groups, ajax_delete_groups, ajax_import_groups, ajax_export_groups
from .views import ajax_add_favorite_groups, ajax_delete_group_favorite, Mailings

from .views import ajax_add_group_item, ajax_list_group_item, ajax_grid_group_item, ajax_delete_group_items

from .views import Commands, CommandAdd, CommandUpdate, CommandsFavorite, CommandDetail
from .views import ajax_list_commands, ajax_grid_commands, ajax_delete_commands
from .views import ajax_command_new_detail
from .views import ajax_add_favorite_commands, ajax_delete_command_favorite
from .views import ajax_command_record_datetime, ajax_delete_lists, MailingDetail, MailingAdd, MailingUpdate, ajax_mail_list, MailListDetail

from .views import Boxs, BoxsFavorite, BoxAdd, BoxUpdate, ajax_get_detail_sub_contact, ajax_get_detail_nest_sub_contact, MailListing, ajax_add_maillist
from .views import ajax_import_boxs, ajax_delete_boxs, ajax_list_boxs, ajax_grid_boxs, ajax_add_sub_contact, ajax_get_sub_contact, ajax_delete_sub_contact
from .views import ajax_add_favorite_boxs, ajax_delete_box_favorite, ajax_quantity, ajax_delete_subproduct, ajax_add_subproduct, ajax_subproduct_list, ajax_delete_mailings, ajax_chatter_leads, ajax_chatter_comment

urlpatterns = [
	url(r'^$', Home.as_view(), name='index'),
	url(r'^login/$', LoginView.as_view(), name='login'),
	url(r'^logout/$', LogoutView.as_view(), name='logout'),
	url(r'^profile/(?P<pk>\d+)/$', Profile.as_view(), name='profile'),
	url(r'^users/$', Users.as_view(), name='users'),
    url(r'^users/role/(?P<pk>\d+)/$', Role.as_view(), name='role'),

	url(r'^ajax-delete-user/$', ajax_delete_user, name='ajax-delete-user'),
	url(r'^ajax-add-user/$', ajax_add_user, name='ajax-add-user'),
    url(r'^ajax-update-user/$', ajax_update_user, name='ajax-update-user'),
	url(r'^ajax-reset-user/$', ajax_reset_user, name='ajax-reset-user'),
    url(r'^ajax-reset-user1/$', ajax_reset_user1, name='ajax-reset-user1'),

	url(r'^reset/password/$', PasswordResetView.as_view(template_name='password_reset_form.html', email_template_name='password_reset_email.html'), name='password_reset'),
    url(r'^reset/password/reset/done/$', PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    url(r'^reset/done/$', PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    url(r'^mailings/$', Mailings.as_view(), name='mailings'),
    url(r'^ajax-add-lists/$', ajax_add_maillist, name='ajax-add-lists'),
    url(r'^maillist/$', MailListing.as_view(), name='maillist'),
    url(r'^ajax-delete-lists/$', ajax_delete_lists, name='ajax-delete-lists'),
    url(r'^mailings-detail/(?P<pk>\d+)$', MailingDetail.as_view(), name='mailings-detail'),
    url(r'^new-mailings/$', MailingAdd.as_view(), name='new-mailings'),
    url(r'^ajax-delete-mailings/$', ajax_delete_mailings, name='ajax-delete-mailings'),
    url(r'^ajax-mail-list/$', ajax_mail_list, name='ajax-mail-list'),
    url(r'^update-mailings/(?P<pk>\d+)/$', MailingUpdate.as_view(), name='update-mailings'),
    url(r'^detail-maillist/(?P<pk>\d+)/$', MailListDetail.as_view(), name='detail-maillist'),

    url(r'^suppliers/$', Suppliers.as_view(), name='suppliers'),
    url(r'^subproduct/$', SubProducts.as_view(), name='subproduct'),
    url(r'^suppliers/favorite/(?P<pk>\d+)$', SuppliersFavorite.as_view(), name='favor-supplier'),
    url(r'^new-supplier/$', SupplierAdd.as_view(), name='new-supplier'),
    url(r'^ajax-add-sub-contact/$', ajax_add_sub_contact, name='ajax-add-sub-contact'),
    url(r'^ajax-delete-sub-contact/$', ajax_delete_sub_contact, name='ajax-delete-sub-contact'),
    url(r'^ajax-get-sub-contact/$', ajax_get_sub_contact, name='ajax-get-sub-contact'),
    url(r'^ajax-get-detail-sub-contact/$', ajax_get_detail_sub_contact, name='ajax-get-detail-sub-contact'),
    url(r'^ajax-get-detail-nest-sub-contact/$', ajax_get_detail_nest_sub_contact, name='ajax-get-detail-nest-sub-contact'),
    url(r'^ajax-import-contacts/$', ajax_import_contacts, name='ajax-import-contacts'),
    url(r'^ajax-subproduct-list/$', ajax_subproduct_list, name='ajax-subproduct-list'),
    url(r'^ajax-export-contacts/$', ajax_export_contacts, name='ajax-export-contacts'),
    url(r'^new-supplier/people/(?P<pk>\d+)$', SupplierContactAdd.as_view(), name='new-contact-supplier'),
    url(r'^update-supplier/(?P<pk>\d+)/$', SupplierUpdate.as_view(), name='update-supplier'),
    url(r'^detail-supplier/(?P<pk>\d+)/$', SupplierDetail.as_view(), name='detail-supplier'),

    url(r'^ajax-list-contacts/$', ajax_list_contacts, name='ajax-list-contacts'),
    url(r'^ajax-grid-contacts/$', ajax_grid_contacts, name='ajax-grid-contacts'),
    url(r'^ajax-delete-contacts/$', ajax_delete_contacts, name='ajax-delete-contacts'),

    url(r'^ajax-add-contact-favorite/$', ajax_add_contact_favorite, name='ajax-add-contact-favorite'),
    url(r'^ajax-delete-contact-favorite/$', ajax_delete_contact_favorite, name='ajax-delete-contact-favorite'),



	url(r'^leads/$', Leads.as_view(), name='leads'),
    url(r'^leads/favorite/(?P<pk>\d+)$', LeadsFavorite.as_view(), name='favor-leads'),
    url(r'^new-lead/$', LeadAdd.as_view(), name='new-lead'),
    url(r'^ajax-import-leads/$', ajax_import_leads, name='ajax-import-leads'),
    url(r'^ajax-export-leads/$', ajax_export_leads, name='ajax-export-leads'),
    url(r'^ajax-export-clients/$', ajax_export_clients, name='ajax-export-clients'),
    url(r'^new-lead/people/(?P<pk>\d+)$', LeadContactAdd.as_view(), name='new-contact-lead'),
    url(r'^update-lead/(?P<pk>\d+)/$', LeadUpdate.as_view(), name='update-lead'),
    url(r'^detail-lead/(?P<pk>\d+)/$', LeadDetail.as_view(), name='detail-lead'),
    url(r'^ajax-chatter-leads/$', ajax_chatter_leads, name='ajax-chatter-leads'),
    url(r'^ajax-chatter-comment/$', ajax_chatter_comment, name='ajax-chatter-comment'),

    url(r'^ajax-list-leads/$', ajax_list_leads, name='ajax-list-leads'),
    url(r'^ajax-grid-leads/$', ajax_grid_leads, name='ajax-grid-leads'),
    
    url(r'^ajax-list-client-leads/$', ajax_list_client_leads, name='ajax-list-client-leads'),
    url(r'^ajax-grid-client-leads/$', ajax_grid_client_leads, name='ajax-grid-client-leads'),
    url(r'^ajax-transform-client-lead/$', ajax_transform_client_lead, name='ajax-transform-client-lead'),


    url(r'^ajax-delete-leads/$', ajax_delete_leads, name='ajax-delete-leads'),

    url(r'^ajax-add-lead-favorite/$', ajax_add_lead_favorite, name='ajax-add-lead-favorite'),
    url(r'^ajax-delete-lead-favorite/$', ajax_delete_lead_favorite, name='ajax-delete-lead-favorite'),

    url(r'^ajax-send-lead-emails/$', ajax_send_lead_emails, name='ajax-send-lead-emails'),

    url(r'^ajax-add-lead-address/$', ajax_add_lead_address, name='ajax-add-lead-address'),
    url(r'^ajax-get-lead-address/$', ajax_get_lead_address, name='ajax-get-lead-address'),
    url(r'^ajax-delete-lead-address/$', ajax_delete_lead_address, name='ajax-delete-lead-address'),

	url(r'^stocks/$', Stocks.as_view(), name='stocks'),
    url(r'^stocks_quantity/$', ajax_quantity, name='stocks_quantity'),
	url(r'^stocks/favorite/(?P<pk>\d+)$', StocksFavorite.as_view(), name='favor-stocks'),
	url(r'^ajax-import-stocks/$', ajax_import_stocks, name='ajax-import-stocks'),
    url(r'^ajax-export-stocks/$', ajax_export_stocks, name='ajax-export-stocks'),
    url(r'^new-stock/$', StockAdd.as_view(), name='new-stock'),
    url(r'^update-stock/(?P<pk>\d+)/$', StockUpdate.as_view(), name='update-stock'),
    url(r'^edit-stock/$', StockTemp.as_view(), name='edit-stock'),
    url(r'^up-stock/(?P<pk>\d+)/$', StockUpTemp.as_view(), name='up-stock'),
    url(r'^ajax-delete-stocks/$', ajax_delete_stocks, name='ajax-delete-stocks'),
    url(r'^ajax-list-stocks/$', ajax_list_stocks, name='ajax-list-stocks'),
    url(r'^ajax-grid-stocks/$', ajax_grid_stocks, name='ajax-grid-stocks'),
    url(r'^ajax-add-favorite-stocks/$', ajax_add_favorite_stocks, name='ajax-add-favorite-stocks'),
    url(r'^ajax-delete-stock-favorite/$', ajax_delete_stock_favorite, name='ajax-delete-stock-favorite'),
    
    ##########
    url(r'^boxs/$', Boxs.as_view(), name='boxs'),
    url(r'^boxs/favorite/(?P<pk>\d+)$', BoxsFavorite.as_view(), name='favor-boxs'),
    url(r'^ajax-import-boxs/$', ajax_import_boxs, name='ajax-import-boxs'),
    url(r'^new-box/$', BoxAdd.as_view(), name='new-box'),
    url(r'^update-box/(?P<pk>\d+)/$', BoxUpdate.as_view(), name='update-box'),
    url(r'^ajax-delete-boxs/$', ajax_delete_boxs, name='ajax-delete-boxs'),
    url(r'^ajax-list-boxs/$', ajax_list_boxs, name='ajax-list-boxs'),
    url(r'^ajax-grid-boxs/$', ajax_grid_boxs, name='ajax-grid-boxs'),
    url(r'^ajax-add-favorite-boxs/$', ajax_add_favorite_boxs, name='ajax-add-favorite-boxs'),
    url(r'^ajax-delete-box-favorite/$', ajax_delete_box_favorite, name='ajax-delete-box-favorite'),
    #############

    url(r'^groups/$', Groups.as_view(), name='groups'),
    url(r'^groups/favorite/(?P<pk>\d+)$', GroupsFavorite.as_view(), name='favor-groups'),
    url(r'^new-group/$', GroupAdd.as_view(), name='new-group'),
    url(r'^ajax-import-groups/$', ajax_import_groups, name='ajax-import-groups'),
    url(r'^ajax-export-groups/$', ajax_export_groups, name='ajax-export-groups'),
    url(r'^update-group/(?P<pk>\d+)/$', GroupUpdate.as_view(), name='update-group'),
    url(r'^detail-group/(?P<pk>\d+)/$', GroupDetail.as_view(), name='detail-group'),
    url(r'^ajax-delete-groups/$', ajax_delete_groups, name='ajax-delete-groups'),

    url(r'^ajax-list-groups/$', ajax_list_groups, name='ajax-list-groups'),
    url(r'^ajax-grid-groups/$', ajax_grid_groups, name='ajax-grid-groups'),

    url(r'^ajax-add-favorite-groups/$', ajax_add_favorite_groups, name='ajax-add-favorite-groups'),
    url(r'^ajax-delete-group-favorite/$', ajax_delete_group_favorite, name='ajax-delete-group-favorite'),

    url(r'^ajax-add-group-item/$', ajax_add_group_item, name='ajax-add-group-item'),
    url(r'^ajax-delete-group-items/$', ajax_delete_group_items, name='ajax-delete-group-items'),
    url(r'^ajax-list-group-item/$', ajax_list_group_item, name='ajax-list-group-item'),
    url(r'^ajax-grid-group-item/$', ajax_grid_group_item, name='ajax-grid-group-item'),


    url(r'^commands/$', Commands.as_view(), name='commands'),
    url(r'^commands/favorite/(?P<pk>\d+)$', CommandsFavorite.as_view(), name='favor-commands'),
    url(r'^new-command/$', CommandAdd.as_view(), name='new-command'),
    url(r'^detail-command/(?P<pk>\d+)/$', CommandDetail.as_view(), name='detail-command'),
    url(r'^ajax-command-new-detail/$', ajax_command_new_detail, name='ajax-command-new-detail'),
    url(r'^update-command/(?P<pk>\d+)/$', CommandUpdate.as_view(), name='update-command'),
    url(r'^ajax-list-commands/$', ajax_list_commands, name='ajax-list-commands'),
    url(r'^ajax-grid-commands/$', ajax_grid_commands, name='ajax-grid-commands'),
    url(r'^ajax-delete-commands/$', ajax_delete_commands, name='ajax-delete-commands'),
    url(r'^ajax-add-favorite-commands/$', ajax_add_favorite_commands, name='ajax-add-favorite-commands'),
    url(r'^ajax-delete-command-favorite/$', ajax_delete_command_favorite, name='ajax-delete-command-favorite'),

    url(r'^ajax-command-record-datetime/$', ajax_command_record_datetime, name='ajax-command-record-datetime'),

    url(r'^category/$', Categories.as_view(), name='category'),
    url(r'^ajax-add-category/$', ajax_add_category, name='ajax-add-category'),
    url(r'^ajax-add-subproduct/$', ajax_add_subproduct, name='ajax-add-subproduct'),
    url(r'^ajax-add-provider/$', ajax_add_provider, name='ajax-add-provider'),
    url(r'^ajax-delete-category/$', ajax_delete_category, name='ajax-delete-category'),
    url(r'^ajax-delete-subproduct/$', ajax_delete_subproduct, name='ajax-delete-subproduct'),

    url(r'^wallstype/$', WallsType.as_view(), name='wallstype'),
    url(r'^ajax-add-wallstype/$', ajax_add_wallstype, name='ajax-add-wallstype'),
    url(r'^ajax-delete-wallstype/$', ajax_delete_wallstype, name='ajax-delete-wallstype'),

    url(r'^castors/$', Castors.as_view(), name='castors'),
    url(r'^ajax-add-castor/$', ajax_add_castor, name='ajax-add-castor'),
    url(r'^ajax-delete-castor/$', ajax_delete_castor, name='ajax-delete-castor'),

    url(r'^colors/$', Colors.as_view(), name='colors'),
    url(r'^ajax-add-color/$', ajax_add_color, name='ajax-add-color'),
    url(r'^ajax-delete-color/$', ajax_delete_color, name='ajax-delete-color'),

    url(r'^drawers/$', Drawers.as_view(), name='drawers'),
    url(r'^ajax-add-drawer/$', ajax_add_drawer, name='ajax-add-drawer'),
    url(r'^ajax-delete-drawer/$', ajax_delete_drawer, name='ajax-delete-drawer'),

    url(r'^strips/$', Strips.as_view(), name='strips'),
    url(r'^ajax-add-strip/$', ajax_add_strip, name='ajax-add-strip'),
    url(r'^ajax-delete-strip/$', ajax_delete_strip, name='ajax-delete-strip'),

    url(r'^locations/$', Locations.as_view(), name='locations'),
    url(r'^ajax-add-location/$', ajax_add_location, name='ajax-add-location'),
    url(r'^ajax-delete-location/$', ajax_delete_location, name='ajax-delete-location'),

    url(r'^locks/$', Locks.as_view(), name='locks'),
    url(r'^ajax-add-lock/$', ajax_add_lock, name='ajax-add-lock'),
    url(r'^ajax-delete-lock/$', ajax_delete_lock, name='ajax-delete-lock'),

    url(r'^tasks/$', Tasks.as_view(), name='tasks'),
    url(r'^ajax-add-task/$', ajax_add_task, name='ajax-add-task'),
    url(r'^ajax-delete-task/$', ajax_delete_task, name='ajax-delete-task'),
]