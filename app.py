from flask import Flask, render_template
app = Flask(__name__)

# TODO : make routes modular by creating a python 
#        file handling any specific page route 

# example of route
@app.route('/')
def home_page():
    return render_template('index.html')

# login page route
@app.route('/login')
def login_page():
    return "Login Page"

if __name__ == "__main__":
    # run the web application
    app.run(debug=True)

