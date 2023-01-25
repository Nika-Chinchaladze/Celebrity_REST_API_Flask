from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from random import choice
import os

app = Flask(__name__)

# BECOME APP BOOTSTRAP COMPATIBLE:
Bootstrap(app)

# CREATE SQLITE3 DATABASE:
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myData.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# CREATE TABLE INSIDE DATABASE:
class Information(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=True)
    age = db.Column(db.Integer, nullable=False)
    movie_genre = db.Column(db.String, nullable=False)
    followers = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String, nullable=True)

    def generate_dictionary(self):
        my_dictionary = {}
        for column in self.__table__.columns:
            my_dictionary[column.name] = getattr(self, column.name)
        return my_dictionary


@app.route("/")
def home_page():
    return "<a style='text-decoration: none; display: block; text-align: center; font-size: 25px; color: blue;' " \
           "href='https://documenter.getpostman.com/view/25457791/2s8ZDcyzUY' " \
           "target='_blank'>View Celebrity API Documentation</a>"


@app.route("/all")
def all_page():
    my_data = Information.query.all()
    return jsonify(
        celebrity_data=[record.generate_dictionary() for record in my_data]
    )


@app.route("/random")
def random_page():
    celebrity_data = Information.query.all()
    return jsonify(
        data=choice(celebrity_data).generate_dictionary()
    )


@app.route("/search/<string:category>")
def search_page(category):
    my_data = []
    # when category type is provided - below logic will be executed:
    if category == "id":
        celebrity_id = request.args.get("celebrity_id")
        my_data = Information.query.get(celebrity_id)
        return jsonify(
            data=my_data.generate_dictionary()
        )
    elif category == "first_name":
        celebrity_name = request.args.get("celebrity_name")
        my_data = Information.query.filter_by(first_name=celebrity_name).all()
    elif category == "last_name":
        celebrity_surname = request.args.get("celebrity_surname")
        my_data = Information.query.filter_by(last_name=celebrity_surname).all()
    elif category == "gender":
        celebrity_gender = request.args.get("celebrity_gender")
        my_data = Information.query.filter_by(gender=celebrity_gender).all()
    elif category == "age":
        celebrity_age = request.args.get("celebrity_age")
        operator_type = request.args.get("operator")
        if operator_type == "=":
            my_data = Information.query.filter_by(age=int(celebrity_age)).all()
        elif operator_type == ">":
            my_data = db.session.query(Information).filter(Information.age > int(celebrity_age)).all()
        elif operator_type == "<":
            my_data = db.session.query(Information).filter(Information.age < int(celebrity_age)).all()
        elif operator_type == ">=":
            my_data = db.session.query(Information).filter(Information.age >= int(celebrity_age)).all()
        elif operator_type == "<=":
            my_data = db.session.query(Information).filter(Information.age <= int(celebrity_age)).all()
        elif operator_type == "!=" or operator_type == "<>":
            my_data = db.session.query(Information).filter(Information.age != int(celebrity_age)).all()
    elif category == "movie_genre":
        celebrity_genre = request.args.get("celebrity_genre")
        my_data = Information.query.filter_by(movie_genre=celebrity_genre).all()
    elif category == "followers":
        celebrity_followers = request.args.get("celebrity_followers")
        operator_type = request.args.get("operator")
        if operator_type == "=":
            my_data = Information.query.filter_by(followers=int(celebrity_followers)).all()
        elif operator_type == ">":
            my_data = db.session.query(Information).filter(Information.followers > int(celebrity_followers)).all()
        elif operator_type == "<":
            my_data = db.session.query(Information).filter(Information.followers < int(celebrity_followers)).all()
        elif operator_type == ">=":
            my_data = db.session.query(Information).filter(Information.followers >= int(celebrity_followers)).all()
        elif operator_type == "<=":
            my_data = db.session.query(Information).filter(Information.followers <= int(celebrity_followers)).all()
        elif operator_type == "!=" or operator_type == "<>":
            my_data = db.session.query(Information).filter(Information.followers != int(celebrity_followers)).all()
    else:
        return jsonify(
            error={
                "Message": "Celebrities Don't have such kind of information attached!"
            }
        )
    # when every parameter is provided - correctly!
    return jsonify(
        data=[celebrity.generate_dictionary() for celebrity in my_data]
    )


@app.route("/add", methods=["POST"])
def add_page():
    new_actor = Information(
        first_name=request.json["first_name"],
        last_name=request.json["last_name"],
        gender=request.json["gender"],
        age=request.json["age"],
        movie_genre=request.json["movie_genre"],
        followers=request.json["followers"],
        img_url=request.json["img_url"]
    )
    db.session.add(new_actor)
    db.session.commit()
    return jsonify(
        success={
            "Message": "Congratulations, New Actor Has Been Added Successfully Into Database!",
            "Status Code": 200
        }
    )


@app.route("/update/<int:celebrity_id>/<string:category>", methods=["PATCH"])
def update_page(celebrity_id, category):
    api_key = request.args.get("api_key")
    current_actor = Information.query.get(celebrity_id)
    my_key = os.environ.get("MY_SECRET_KEY")
    if api_key == my_key:
        if category == "first_name":
            current_actor.first_name = request.args.get("first_name")
        elif category == "last_name":
            current_actor.last_name = request.args.get("last_name")
        elif category == "gender":
            current_actor.gender = request.args.get("gender")
        elif category == "age":
            current_actor.category = request.args.get("age")
        elif category == "movie_genre":
            current_actor.movie_genre = request.args.get("movie_genre")
        elif category == "followers":
            current_actor.followers = request.args.get("followers")
        elif category == "img_url":
            current_actor.img_url = request.args.get("img_url")
        else:
            return jsonify(
                error={
                    "Message": "Category Name is not correct!"
                }
            )

        db.session.commit()
        db.session.close()
        return jsonify(
            success={
                "Message": "Congratulations, Information Has Been Updated Successfully!",
                "Status Code": 200
            }
        )
    else:
        return jsonify(
            error={
                "Message": "Forbidden, api key is not CORRECT!",
                "Status Code": 403
            }
        )


@app.route("/change/<int:celebrity_id>", methods=["PUT"])
def change_page(celebrity_id):
    update_record = Information.query.get(celebrity_id)
    api_key = request.args.get("api_key")
    my_key = os.environ.get("MY_SECRET_KEY")
    if api_key == my_key:
        update_record.first_name = request.args.get("first_name")
        update_record.last_name = request.args.get("last_name")
        update_record.gender = request.args.get("gender")
        update_record.age = request.args.get("age")
        update_record.movie_genre = request.args.get("movie_genre")
        update_record.followers = request.args.get("followers")
        update_record.img_url = request.args.get("img_url")
        db.session.commit()
        db.session.close()
        return jsonify(
            success={
                "Message": "Congratulations, Information Has Been Renewed Completely!",
                "Status Code": 200
            }
        )
    else:
        return jsonify(
            forbidden={
                "Message": "Unfortunately, api key is not CORRECT",
                "Status Code": 403
            }
        )


@app.route("/delete/<int:celebrity_id>", methods=["DELETE"])
def delete_page(celebrity_id):
    delete_record = Information.query.get(celebrity_id)
    api_key = request.args.get("api_key")
    my_key = os.environ.get("MY_SECRET_KEY")
    if api_key == my_key:
        db.session.delete(delete_record)
        db.session.commit()
        db.session.close()
        return jsonify(
            success={
                "Message": "Well Done, Record Has Been Removed Successfully!",
                "Status Code": 200
            }
        )
    else:
        return jsonify(
            forbidden={
                "Message": "Unfortunately, api key is not CORRECT",
                "Status Code": 403
            }
        )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
