from __future__ import division

import json
import logging
import os
import time
from builtins import next
from builtins import str
from datetime import datetime
from io import BytesIO

from dateutil.parser import isoparse
from django.conf import settings
from django.contrib.postgres.aggregates.general import BoolOr
from django.core.cache import cache as django_cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db.models import Count
from django.db.models import F
from django.db.models import Sum
from django.db.models import Value
from django.db.models.expressions import CombinedExpression
from django.utils import timezone
from django_redis.client import DefaultClient
from le_utils.constants import content_kinds
from le_utils.constants import format_presets

from contentcuration.decorators import redis_retry
from contentcuration.models import AssessmentItem
from contentcuration.models import ContentNode
from contentcuration.models import File
from contentcuration.models import FormatPreset
from contentcuration.models import generate_object_storage_name
from contentcuration.models import Language
from contentcuration.models import User
from contentcuration.utils.files import get_thumbnail_encoding


def map_files_to_node(user, node, data):
    """
    Generate files that reference the content node.
    """
    if settings.DEBUG:
        # assert that our parameters match expected values
        assert isinstance(user, User)
        assert isinstance(node, ContentNode)
        assert isinstance(data, list)

    # filter out file that are empty
    valid_data = filter_out_nones(data)

    for file_data in valid_data:
        filename = file_data["filename"]
        checksum, ext1 = os.path.splitext(filename)
        ext = ext1.lstrip(".")

        # Determine a preset if none is given
        kind_preset = FormatPreset.get_preset(file_data["preset"]) or FormatPreset.guess_format_preset(filename)

        file_path = generate_object_storage_name(checksum, filename)
        storage = default_storage

        if not storage.exists(file_path):
            raise IOError('{} not found'.format(file_path))

        try:
            if file_data.get('language'):
                # TODO: Remove DB call per file?
                file_data['language'] = Language.objects.get(pk=file_data['language'])
        except ObjectDoesNotExist:
            invalid_lang = file_data.get('language')
            logging.warning("file_data with language {} does not exist.".format(invalid_lang))
            return ValidationError("file_data given was invalid; expected string, got {}".format(invalid_lang))

        resource_obj = File(
            checksum=checksum,
            contentnode=node,
            file_format_id=ext,
            original_filename=file_data.get('original_filename') or 'file',
            source_url=file_data.get('source_url'),
            file_size=file_data['size'],
            preset=kind_preset,
            language_id=file_data.get('language'),
            uploaded_by=user,
        )
        resource_obj.file_on_disk.name = file_path
        resource_obj.save()

        # Handle thumbnail
        if resource_obj.preset and resource_obj.preset.thumbnail:
            node.thumbnail_encoding = json.dumps({
                'base64': get_thumbnail_encoding(str(resource_obj)),
                'points': [],
                'zoom': 0
            })
            node.save()


def map_files_to_assessment_item(user, assessment_item, data):
    """
    Generate files referenced in given assesment item (a.k.a. question).
    """
    if settings.DEBUG:
        # assert that our parameters match expected values
        assert isinstance(user, User)
        assert isinstance(assessment_item, AssessmentItem)
        assert isinstance(data, list)

    # filter out file that are empty
    valid_data = filter_out_nones(data)

    for file_data in valid_data:
        filename = file_data["filename"]
        checksum, ext = filename.split(".")

        file_path = generate_object_storage_name(checksum, filename)
        storage = default_storage
        if not storage.exists(file_path):
            raise IOError('{} not found'.format(file_path))

        resource_obj = File(
            checksum=checksum,
            assessment_item=assessment_item,
            file_format_id=ext,
            original_filename=file_data.get('original_filename') or 'file',
            source_url=file_data.get('source_url'),
            file_size=file_data['size'],
            preset_id=file_data["preset"],   # assessment_item-files always have a preset
            uploaded_by=user,
        )
        resource_obj.file_on_disk.name = file_path
        resource_obj.save()


def map_files_to_slideshow_slide_item(user, node, slides, files):
    """
    Generate files referenced in given slideshow slide
    """
    for file_data in files:
        filename = file_data["filename"]
        checksum, ext = filename.split(".")

        matching_slide = next((slide for slide in slides if slide.metadata["checksum"] == checksum), None)

        if not matching_slide:
            # TODO(Jacob) Determine proper error type... raise it.
            print("NO MATCH")

        file_path = generate_object_storage_name(checksum, filename)
        storage = default_storage

        if not storage.exists(file_path):
            raise IOError('{} not found'.format(file_path))

        file_obj = File(
            slideshow_slide=matching_slide,
            checksum=checksum,
            file_format_id=ext,
            original_filename=file_data.get("original_filename") or "file",
            source_url=file_data.get("source_url"),
            file_size=file_data["size"],
            preset_id=file_data["preset"],
            uploaded_by=user
        )

        file_obj.file_on_disk.name = file_path
        file_obj.save()


def filter_out_nones(data):
    """
    Filter out any falsey values from data.
    """
    return (d for d in data if d)


def _get_diff_filepath(node_id1, node_id2):
    return os.path.join(settings.DIFFS_ROOT, node_id1, '{}.json'.format(node_id2))


def _get_created_time(node):
    return node.created.strftime('%Y-%m-%d %H:%M:%S')


def get_diff(updated, original):
    jsonpath = _get_diff_filepath(updated.pk, original.pk)
    if default_storage.exists(jsonpath):
        with default_storage.open(jsonpath, 'rb') as jsonfile:
            data = json.load(jsonfile)
            if data['generated'] == _get_created_time(updated):
                return data
    return None


def generate_diff(updated_id, original_id):
    updated = ContentNode.objects.filter(pk=updated_id).first()
    original = ContentNode.objects.filter(pk=original_id).first()

    main_descendants = original.get_descendants() if original else None
    updated_descendants = updated.get_descendants() if updated else None

    original_stats = main_descendants.values('kind_id').annotate(count=Count('kind_id')).order_by() if original else {}
    updated_stats = updated_descendants.values('kind_id').annotate(count=Count('kind_id')).order_by() if updated else {}

    original_file_sizes = main_descendants.aggregate(
        resource_size=Sum('files__file_size'),
        assessment_size=Sum('assessment_items__files__file_size'),
        assessment_count=Count('assessment_items'),
    ) if original else {}

    updated_file_sizes = updated_descendants.aggregate(
        resource_size=Sum('files__file_size'),
        assessment_size=Sum('assessment_items__files__file_size'),
        assessment_count=Count('assessment_items')
    ) if updated else {}

    original_file_size = (original_file_sizes.get('resource_size') or 0) + (original_file_sizes.get('assessment_size') or 0)
    updated_file_size = (updated_file_sizes.get('resource_size') or 0) + (updated_file_sizes.get('assessment_size') or 0)
    original_question_count = original_file_sizes.get('assessment_count') or 0
    updated_question_count = updated_file_sizes.get('assessment_count') or 0

    original_resource_count = original.get_descendants().exclude(kind_id='topic').count() if original else 0
    updated_resource_count = updated.get_descendants().exclude(kind_id='topic').count() if updated else 0

    stats = [
        {
            "field": "date_created",
            "original": original.created.strftime("%x %X") if original else "",
            "changed": updated.created.strftime("%x %X") if updated else "",
        },
        {
            "field": "ricecooker_version",
            "original": original.extra_fields.get('ricecooker_version') if original and original.extra_fields else "",
            "changed": updated.extra_fields.get('ricecooker_version') if updated and updated.extra_fields else "",
        },
        {
            "field": "file_size_in_bytes",
            "original": original_file_size,
            "changed": updated_file_size,
            "difference": updated_file_size - original_file_size,
            "format_size": True,
        },
        {
            "field": "count_resources",
            "original": original_resource_count,
            "changed": updated_resource_count,
            "difference": updated_resource_count - original_resource_count,
        }
    ]

    for kind, name in content_kinds.choices:
        original_kind = original_stats.get(kind_id=kind)['count'] if original and original_stats.filter(kind_id=kind).exists() else 0
        updated_kind = updated_stats.get(kind_id=kind)['count'] if updated and updated_stats.filter(kind_id=kind).exists() else 0
        stats.append({"field": "count_{}s".format(kind), "original": original_kind, "changed": updated_kind, "difference": updated_kind - original_kind})

    # Add number of questions
    stats.append({
        "field": "count_questions",
        "original": original_question_count,
        "changed": updated_question_count,
        "difference": updated_question_count - original_question_count,
    })

    # Add number of subtitles
    original_subtitle_count = main_descendants.filter(files__preset_id=format_presets.VIDEO_SUBTITLE).count() if original else 0
    updated_subtitle_count = updated_descendants.filter(files__preset_id=format_presets.VIDEO_SUBTITLE).count() if updated else 0
    stats.append({
        "field": "count_subtitles",
        "original": original_subtitle_count,
        "changed": updated_subtitle_count,
        "difference": updated_subtitle_count - original_subtitle_count,
    })

    # Do one more check before we write the json file in case multiple tasks were triggered
    # and we need to ensure that we don't overwrite the latest version of the changed diff
    jsondata = get_diff(updated, original)
    creation_time = _get_created_time(updated)

    if not jsondata or jsondata['generated'] <= creation_time:
        jsondata = {
            'generated': creation_time,
            'stats': stats
        }
        jsonpath = _get_diff_filepath(updated_id, original_id)
        default_storage.save(jsonpath, BytesIO(json.dumps(jsondata).encode('utf-8')))

    return jsondata


class ResourceSizeCache:
    """
    Helper class for managing Resource size cache.

    If the django_cache is Redis, then we use the lower level Redis client to use
    its hash commands, HSET and HGET, to ensure we can store lots of data in performant way
    """
    def __init__(self, node, cache=None):
        self.node = node
        self.cache = cache or django_cache

    @property
    def redis_client(self):
        """
        Gets the lower level Redis client, if the cache is a Redis cache

        :rtype: redis.client.StrictRedis
        """
        redis_client = None
        cache_client = getattr(self.cache, 'client', None)
        if isinstance(cache_client, DefaultClient):
            redis_client = cache_client.get_client(write=True)
        return redis_client

    @property
    def hash_key(self):
        # only first four characters
        return "resource_size:{}".format(self.node.pk[:4])

    @property
    def size_key(self):
        return "{}:value".format(self.node.pk)

    @property
    def modified_key(self):
        return "{}:modified".format(self.node.pk)

    @redis_retry
    def cache_get(self, key):
        if self.redis_client is not None:
            # notice use of special `HGET`
            # See: https://redis.io/commands/hget
            return self.redis_client.hget(self.hash_key, key)
        return self.cache.get("{}:{}".format(self.hash_key, key))

    @redis_retry
    def cache_set(self, key, val):
        if self.redis_client is not None:
            # notice use of special `HSET`
            # See: https://redis.io/commands/hset
            return self.redis_client.hset(self.hash_key, key, val)
        return self.cache.set("{}:{}".format(self.hash_key, key), val)

    def get_size(self):
        size = self.cache_get(self.size_key)
        return int(size) if size else size

    def get_modified(self):
        modified = self.cache_get(self.modified_key)
        return isoparse(modified) if modified else modified

    def set_size(self, size):
        return self.cache_set(self.size_key, size)

    def set_modified(self, modified):
        return self.cache_set(self.modified_key, modified.isoformat() if isinstance(modified, datetime) else modified)


class ResourceSizeHelper:
    """
    Helper class for calculating resource size
    """
    def __init__(self, node):
        """
        :param node: The contentnode with which to determine resource size
        :type node: ContentNode
        """
        self.node = node

    @property
    def queryset(self):
        """
        :rtype: QuerySet
        """
        qs = self.node.get_descendants(include_self=True)

        if self.node.is_root_node():
            # since root node, remove unneeded filtering
            qs = ContentNode.objects.filter(tree_id=self.node.tree_id)
        # else if it's a leaf node, simplification handled by `get_descendants`

        return File.objects.filter(contentnode__in=qs.filter(complete=True))

    def get_size(self):
        """
        Calculates the size of the resource and it's descendants

        SQL:
            SELECT SUM(file_size)
            FROM (
                SELECT DISTINCT
                    checksum,
                    file_size
                FROM contentcuration_file
                WHERE contentnode_id IN ( SELECT id FROM contentcuration_contentnode WHERE ... )
            ) subquery
            ;

        :return: An integer representing the resource size
        """
        sizes = self.queryset.values("checksum").distinct().aggregate(resource_size=Sum("file_size"))
        return sizes['resource_size']

    def modified_since(self, compare_datetime):
        """
        Determines if resources have been modified since ${compare_datetime}

        SQL:
            SELECT BOOL_OR(modified > ${compare_datetime})
            FROM (
                SELECT
                    modified_at
                FROM contentcuration_file
                WHERE contentnode_id IN ( SELECT id FROM contentcuration_contentnode WHERE ... )
            ) subquery
            ;

        :
        :param compare_datetime: The datetime with which to compare.
        :return: A boolean indicating whether or not resources have been modified since the datetime
        """
        compare_datetime = compare_datetime.isoformat() if isinstance(compare_datetime, datetime) else compare_datetime
        result = self.queryset.aggregate(
            modified_since=BoolOr(CombinedExpression(F('modified'), '>', Value(compare_datetime)))
        )
        return result['modified_since']


STALE_MAX_CALCULATION_SIZE = 5000


def calculate_resource_size(node, force=False):
    """
    Function that calculates the total file size of all files of the specified node and it's
    descendants, if they're marked complete

    :param node: The ContentNode for which to calculate resource size.
    :param force: A boolean to force calculation if node is too big and would otherwise do so async
    :return: A tuple of (size, stale)
    :rtype: (int, bool)
    """
    cache = ResourceSizeCache(node)
    db = ResourceSizeHelper(node)

    size = None if force else cache.get_size()
    modified = None if force else cache.get_modified()

    # since we added file.modified as nullable, if the result is None/Null, then we know that it
    # hasn't been modified since our last cached value, so we only need to check is False
    if size is not None and modified is not None and db.modified_since(modified) is False:
        # use cache if not modified since cache modified timestamp
        return size, False

    # if the node is too big to calculate its size right away, we return "stale"
    if not force and node.get_descendant_count() > STALE_MAX_CALCULATION_SIZE:
        return size, True

    start = time.time()

    # do recalculation, marking modified time before starting
    now = timezone.now()
    size = db.get_size()
    cache.set_size(size)
    cache.set_modified(now)
    elapsed = time.time() - start

    # log how long calculation took
    msg = "Resource size recalculation for {} took {}s".format(node.pk, elapsed)
    if elapsed > 5:
        logging.warning(msg)
    else:
        logging.info(msg)

    return size, False
