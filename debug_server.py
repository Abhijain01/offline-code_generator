from app import app, load_generator

if __name__ == '__main__':
    load_generator()
    print("Starting Debug Web Server at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
