#!/usr/bin/env python
# coding: utf-8

from flask import Flask, abort, render_template
from neo4j.v1 import GraphDatabase


app = Flask(__name__)

# Set up a driver for the local graph database.
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))


def match_movies(tx):
    return tx.run("MATCH (movie:Movie) "
                  "RETURN movie.title AS title, movie.released AS released "
                  "ORDER BY movie.title").data()


def match_movie(tx, title):
    record = tx.run("MATCH (movie:Movie) "
                    "WHERE movie.title = $title "
                    "RETURN movie", title=title).single()
    return dict(record[0]) if record else None


@app.route("/")
def get_index():
    """ Show the index page.
    """
    return render_template("index.html")


@app.route("/movie/")
def get_movie_list():
    """ Fetch a list of all movies, ordered by title and render
    them within the 'movie_list' template.
    """
    with driver.session() as session:
        return render_template("movie_list.html", movies=session.read_transaction(match_movies))


@app.route("/movie/<title>")
def get_movie(title):
    """ Display details of a particular movie.
    """
    with driver.session() as session:
        movie = session.read_transaction(match_movie, title)
        if movie is None:
            abort(404, "Movie not found")
        return render_template("movie.html", movie=movie)
