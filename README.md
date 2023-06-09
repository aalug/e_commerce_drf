﻿# Django REST framework e-commerce app

The app is built with the **Django REST framework**.

The app uses:

- Docker
- Postgres
- Elasticsearch
- Celery
- RabbitMQ
- Redis
- drf-spectacular for documentation

## Getting started

1. Clone the repository.
2. Rename `.env.sample` to `.env` and replace the values
3. Run in your terminal `docker-compose up --build`
4. Now everything should be set up and app's documentation available on http://localhost:8000/api/docs/


## Sample data
To get sample data:
1. With running containers run `docker ps` and get the ID of the app container
2. Run `docker exec -itu 0 <container ID> sh` to get access to the container's shell
3. In the bash terminal, run the following commands:
- `python manage.py populate_store` to create in the database objects for a book store (this is just an example, database was not designed with this in mind, it was created as a universal database)

or

- `python manage.py makemigrations` and `python manage.py migrate` first. Then:
- `python manage.py loaddata category_fixtures.json`
- `python manage.py populate_products`
- `python manage.py populate_brands`
- `python manage.py populate_product_inventories`
- `python manage.py populate_stock`
- `python manage.py populate_attributes`
- `python manage.py populate_product_images` 
to create sample data for each model individually.

## Testing

To run tests:
1. If containers are not running, run in your terminal `docker-compose up`
2. In the second terminal tab, run `docker ps` and get the ID of the app container
3. Run `docker exec -itu 0 <container ID> sh` to get access to the container's shell
4. Run `python manage.py test` to run all tests or `python manage.py test <app-name>.tests` to run tests for a specific
   app


## Elasticsearch
To create indexes run in the container's shell `python manage.py search_index --rebuild`


## API Endpoints

All endpoints are available on http://localhost:8000/api/docs/.
After running containers, this will provide you with complete and easy-to-use documentation.
It also gives the option to use every endpoint of this API.

#### Users app

- Use `/api/users/create/` to create a new user
- Then use `/api/users/token/` to create a token for the created user
- Use `/api/users/profile/` to retrieve user details and update password and user profile details
- Use `/api/users/forgot-password/` to send an email with a link to reset the password

#### Inventory app
- Use `/api/inventory/main-categories/` to list all main categories - that do not have a parent category
- Use `/api/inventory/categories/{id}/` to get category with all children categories
- Use `/api/inventory/products/` to list all products.
Available `query_params`:
  + `attribute-values` - a list of ids of attribute values. For example `?attribute-values=1,5,20`
  + `brand` - a list of ids of brands. For example `?brand=1,5,20`
  + `price` - a price range for products in `int,int` format. For example `?price=3,12`
  + `search` - an elasticsearch search feature. For example `?search=foo`
- Use `/api/inventory/products-by-category/{id}/` to list all products from a given category. 
It is handled by the same APIView as `/api/inventory/products/` endpoint, so it also accepts
`query_params` listed above.
- Use `/api/inventory/products/{id}/` to retrieve product details.
- Use `/api/inventory/attribute-values/` to list all product attribute values. 

#### Orders app
- Use `/api/orders/` to create a new order and list all orders of the logged-in user. 


### More Information
This app uses [djangorestframework-camel-case](https://github.com/vbabiy/djangorestframework-camel-case) to enable the server to send and receive data in a format that is compatible with TypeScript. This package provides support for camel-case style serialization and deserialization, which is appropriate for the conventions used in Vue.js.
