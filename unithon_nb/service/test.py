import logging

from unithon_nb import app, mongo3
from unithon_nb.util.trans import as_json

logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
@as_json
def save_log_to_server():
    return {
        'success': True
    }
