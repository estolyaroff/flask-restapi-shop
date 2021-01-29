flask restapi shop
##################

**Requirements**

* Python 3+
* Virtualenv
* Docker


**Create virtual environment & install requirements**

    virtualenv <envname> -p python3
    
    source <envname>/bin/activate
    
    pip install -r requirements.txt
    
**Add dotenv to project root**

You should create a .env file on the project root using the following format:

  JWT_SECRET_KEY = "random string"
    
**Create Postgres DB using Docker**

  docker run -d --name restapi-shop -e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5432:5432 postgres

**Make migrations**

    python manager.py db init
    
    python manager.py db migrate
    
    python manager.py db upgrade

**Fill the database with test data**
  
    python data_upload.py
  
**Run**

    python run.py


This example provides the following API structure:

==============================  ======  =============  ===========================  =========================== ===========================
URL                             method  endpoint       Usage                        Access                      Data
==============================  ======  =============  ===========================  =========================== ===========================
/api/signup/                    POST    SignupApi      Create account               free access                 {"str:email", "str:password"}
/api/login/                     POST    LoginApi       Login                        free access                 {"str:email", "str:password"}
/api/catalog/<int:page>         GET     CatalogView    Get a list of all products   free access                 
/api/category/<int:id>          GET     CategoryView   Get category information     token                       
/api/category/                  POST    CategoryView   Create category              token                       {"str:category_name", "str:category_description"}
/api/category/<int:id>          PUT     CategoryView   Update category              token                       {"str:category_name", "str:category_description"}
/api/category/<int:id>          DELETE  CategoryView   Delete category              token
/api/product/<int:id>           GET     ProductView    Get product information      token
/api/product/                   POST    ProductView    Get product information      token                       {"str:name", "str:description", "float:price", "int:quantity", "int:category_id"}
/api/product/<int:id>           PUT     ProductView    Get product information      token                       {"str:name", "str:description", "float:price", "int:quantity", "int:category_id"}
/api/product/<int:id>           DELETE  ProductView    Get product information      token
==============================  ======  =============  ===========================  =========================== ===========================

