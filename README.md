# Udacity-Item-Catalog

Udacity Full Stack Web Developer Nanodegree Project

# About

This Udacity-Item-Catalog project is a Shopping Catalog. The Shopping Catalog consists of Product Categories and Product Items in each Product Category. All users can display catalog but only logged in users can add, edit or delete the catalog. Users login via their Github accounts.

Logged in users can:

- add new categories
- edit and delete categories they created
- add items to categories they created
- edit or delete the items they created

## Prerequisites

- Python 3
- Flask
- SQLAlchemy
- requests_oauthlib library

## Populate the database

To create and  populate the database, run populate_db.py file

	python3 populate_db.py

## Run the project
Run project with

	python3 application.py
and access from

	http://localhost:5000/


## JSON Endpoints

Catalog JSON - Displays the categories and the items belongs to the categories:
`/catalog_json`

Items JSON - Displays all the items:
`/items_json`
