import os
from unithon_nb import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8009))
    app.run('127.0.0.1', port=port)
