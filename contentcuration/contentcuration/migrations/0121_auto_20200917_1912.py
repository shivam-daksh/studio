# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-17 19:12
from __future__ import unicode_literals

from django.db import migrations
from django.db import models

import contentcuration.models

class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('contentcuration', '0120_auto_20200917_1912'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddIndex(
                    model_name="contentnode",
                    index=models.Index(fields=["~modified"], name="node_modified_desc_idx"),
                ),
            ],
            database_operations=[
                # operation to run custom SQL command (check the output of `sqlmigrate`
                # to see the auto-generated SQL, edit as needed)
                migrations.RunSQL(
                    sql='CREATE INDEX CONCURRENTLY "{index_name}" ON "contentcuration_contentnode" (modified DESC NULLS LAST);'.format(
                        index_name=contentcuration.models.NODE_MODIFIED_DESC_INDEX_NAME
                    ),
                    reverse_sql='DROP INDEX "{index_name}"'.format(
                        index_name=contentcuration.models.NODE_MODIFIED_DESC_INDEX_NAME
                    ),
                ),
            ],
        ),
    ]
