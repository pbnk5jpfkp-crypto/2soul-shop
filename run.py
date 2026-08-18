import os
from app import app, init_db

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run app
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=5000)