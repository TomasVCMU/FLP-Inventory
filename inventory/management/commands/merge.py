#!/usr/bin/python
from django.core.management.base import BaseCommand
from inventory.models import Item, Category, ItemTransaction
import openpyxl

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('items_to_merge')

    def handle(self, *args, **options):
        ITEMS_TO_MERGE_FILE_PATH = options['items_to_merge']

        inventory_sheet = openpyxl.load_workbook(ITEMS_TO_MERGE_FILE_PATH).active

        for r in inventory_sheet.iter_rows(min_row=2): # skip header
            new_item_name = r[0].value
            tmp = [Item.objects.filter(name__exact=c.value) for c in r[1:] if c is not None]
            items_to_merge = []
            for qs in tmp:
                if len(qs) != 0:
                    items_to_merge.append(qs[0])

            print("new item name: ", new_item_name)
            print("items to merge: ", items_to_merge)

            # assumption that they're all the same category to begin with and will all have same category again
            quantity = sum(item.quantity for item in items_to_merge)
            new_item = Item.objects.create(category=items_to_merge[0].category, name=new_item_name, quantity=quantity)

            print("new item quantity: ", quantity)
            print("new item: ", new_item)

            for item in items_to_merge:
                qs = ItemTransaction.objects.filter(item__exact=item)
                if len(qs) != 0:
                    transaction = qs[0]
                    transaction.item = new_item
                    transaction.save()
                    print("transaction, transitem: ", transaction, transaction.item)
                else:
                    print("not found: ", item, item.name)

            # search for these in transactions and replace them
            # delete old items

            