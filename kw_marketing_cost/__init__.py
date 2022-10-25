import logging

from . import models
from . import report
from . import wizard

_logger = logging.getLogger(__name__)


def kw_utm_str_post_init_hook(cr, registry):
    cr.execute(
        'UPDATE crm_lead '
        'SET kw_utm_str = concat_ws('
        '\'_\', coalesce(medium_id, 0), coalesce(source_id, 0), '
        'coalesce(campaign_id, 0));')
    cr.execute(
        'UPDATE sale_order '
        'SET kw_utm_str = concat_ws('
        '\'_\', coalesce(medium_id, 0), coalesce(source_id, 0), '
        'coalesce(campaign_id, 0));')
    cr.execute(
        'UPDATE account_move '
        'SET kw_utm_str = concat_ws('
        '\'_\', coalesce(medium_id, 0), coalesce(source_id, 0), '
        'coalesce(campaign_id, 0));')
