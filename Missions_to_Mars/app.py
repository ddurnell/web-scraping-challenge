from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# create the flask app
app = Flask(__name__)

# declare the database
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

# the base route
@app.route('/')
def index():
    mars = mongo.db.mars.find_one()
    # print(mars['facts'])
    return render_template('index.html', mars=mars)

# the scraping route, which redirects to the base app
@app.route('/scrape')
def scrape():
    mars = mongo.db.mars
    data = scrape_mars.scrape()
    mars.update(
        {},
        data,
        upsert=True
    )
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
