from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from .models import Contact, User, Client, Location, Category, Stock, Mailing
from cities_light.models import Country

class ContactResource(resources.ModelResource):
    user = fields.Field(
        column_name='owner',
        attribute='user',
        widget=ForeignKeyWidget(User, 'name'))
    parent = fields.Field(
        column_name='company',
        attribute='parent',
        widget=ForeignKeyWidget(Contact, 'name'))
    country = fields.Field(
        column_name='country',
        attribute='country',
        widget=ForeignKeyWidget(Country, 'name'))
    class Meta:
        model = Contact
        fields = ('name', 'nif', 'address', 'email', 'telephone', 'mobile', 'web', 'notes', 'products', 'country', 'user', 'parent')
        export_order = ('name', 'nif', 'address', 'email', 'telephone', 'mobile', 'web', 'notes', 'products', 'country', 'user', 'parent')

class LeadResource(resources.ModelResource):
    user = fields.Field(
        column_name='owner',
        attribute='user',
        widget=ForeignKeyWidget(User, 'name'))
    parent = fields.Field(
        column_name='company',
        attribute='parent',
        widget=ForeignKeyWidget(Client, 'name'))
    country = fields.Field(
        column_name='country',
        attribute='country',
        widget=ForeignKeyWidget(Country, 'name'))
    class Meta:
        model = Client
        fields = ('name', 'nif', 'email', 'telephone', 'mobile', 'web', 'notes', 'products', 'country', 'user', 'parent')
        export_order = ('name', 'nif', 'email', 'telephone', 'mobile', 'web', 'notes', 'products', 'country', 'user', 'parent')

    def get_queryset(self):
        return self._meta.model.objects.filter(b_client=False)

class ClientResource(resources.ModelResource):
    user = fields.Field(
        column_name='owner',
        attribute='user',
        widget=ForeignKeyWidget(User, 'name'))
    parent = fields.Field(
        column_name='company',
        attribute='parent',
        widget=ForeignKeyWidget(Client, 'name'))
    country = fields.Field(
        column_name='country',
        attribute='country',
        widget=ForeignKeyWidget(Country, 'name'))
    class Meta:
        model = Client
        fields = ('name', 'nif', 'email', 'telephone', 'mobile', 'web', 'notes', 'products', 'country', 'user', 'parent')
        export_order = ('name', 'nif', 'email', 'telephone', 'mobile', 'web', 'notes', 'products', 'country', 'user', 'parent')

    def get_queryset(self):
        return self._meta.model.objects.filter(b_client=True)

class StockResource(resources.ModelResource):
    location = fields.Field(
        column_name='location',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name'))
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name'))
    class Meta:
        model = Stock
        fields = ('name', 'reference', 'location', 'width', 'height', 'depth', 'weight', 'category', 'quantity', 'minium')
        export_order = ('name', 'reference', 'location', 'width', 'height', 'depth', 'weight', 'category', 'quantity', 'minium')

    def get_queryset(self):

        preview_query = self._meta.model.objects.filter(b_group=0)
        filtered_ids = preview_query.values_list('id', flat=True)
        
        # raw_query # yangyang
        str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
                SELECT id, quantity, minium from backend_stock \
                UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
                UNION ALL SELECT stock_id as id, SUM(V.valid_quantity) as quantity, 0 as minium FROM purchase_orderitem P LEFT JOIN purchase_orderincomevalid V on V.orderitem_id = P.id group by P.stock_id\
                UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
                UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
                ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")"
        stocks = self._meta.model.objects.raw(str_query)
        
        return stocks

class GroupResource(resources.ModelResource):
    location = fields.Field(
        column_name='location',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name'))
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name'))
    class Meta:
        model = Stock
        fields = ('name', 'reference', 'location', 'width', 'height', 'depth', 'weight', 'category', 'quantity', 'minium')
        export_order = ('name', 'reference', 'location', 'width', 'height', 'depth', 'weight', 'category', 'quantity', 'minium')

    def get_queryset(self):

        preview_query = self._meta.model.objects.filter(b_group=1)
        filtered_ids = preview_query.values_list('id', flat=True)
        
        # raw_query # yangyang
        str_query = "SELECT * FROM (SELECT id, SUM(quantity) as quantity, SUM(minium) as minium FROM (\
            SELECT id, quantity, minium from backend_stock \
            UNION ALL SELECT I.stock_id as id, SUM(-I.quantity*C.quantity) as quantity, 0 as minium FROM backend_command as C INNER JOIN backend_groupitem as I on I.parent_id = C.group_id group by I.stock_id \
            UNION ALL SELECT group_id as id, SUM(quantity) as quantity, 0 as minium FROM backend_command WHERE finished=3 group by group_id\
            UNION ALL SELECT stock_id as id, SUM(-OI.order_quantity) as quantity, 0 as minium FROM outcome_outcome as O LEFT JOIN outcome_outcomeitem as OI on OI.outcome_id = O.id WHERE O.finished='1' group by OI.stock_id\
            UNION ALL SELECT stock_id as id, SUM(quantity) as quantity, 0 as minium FROM adjust_adjustitem  group by stock_id\
            ) GROUP BY id) WHERE id in (" + ','.join(map(str, filtered_ids)) + ")"
        stocks = self._meta.model.objects.raw(str_query)
        
        return stocks

class MailResource(resources.ModelResource):
    
    class Meta:
        model = Mailing
        fields = ('name', 'content', 'date', 'mail_list')
        export_order = ('name', 'content', 'date', 'mail_list')