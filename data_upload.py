from app.catalog.models import Product, Category, ChangeLog
from app import db
from mimesis import Text, Hardware
import random


categories = [
    "Notebooks",
    "Smartphones",
    "TV",
    "Game consoles",
    "Refrigerators",
    "Washing machines"
]

notebooks = [
    "Asus",
    "Macbook Pro",
    "Lenovo",
]

tv = [
    "LG",
    "Sumsung",
    "Sony",
]

consoles = [
    "Xbox",
    "Sony Playstation",
]

refr = [
    "LG",
    "Samsung"
]

wash = [
    "LG",
    "Indesit",
]


def generation_price():
    dollar = random.randint(34, 987)
    cent = random.randint(0, 99)
    return dollar + cent


def generation_qty():
    return random.randint(1, 34)


def upload_test_category(n, d):
    cat = Category(name=n, description=d)
    db.session.add(cat)
    db.session.commit()


def upload_test_product(name, description, price, qty, category_id):
    product = Product(name=name, description=description, price=price, qty=qty)
    c = Category.query.filter_by(id=category_id).first()
    l = ChangeLog(value=product.qty, product_id=product)
    product.changelog.append(l)
    product.categories.append(c)
    db.session.add(product)
    db.session.commit()


def main():
    hard = Hardware()
    text = Text()

    # categories
    for category in categories:
        description = text.text(quantity=3)
        upload_test_category(category, description)

    # Notebooks
    for notebook in notebooks:
        upload_test_product(
            name=notebook,
            description=text.text(quantity=2),
            price=generation_price(),
            qty = generation_qty(),
            category_id = 1,
        )

    # smartphones
    for i in range(12):
        upload_test_product(
            name=hard.phone_model(),
            description=text.text(quantity=2),
            price=generation_price(),
            qty=generation_qty(),
            category_id=2,
        )

    # TV
    for t in tv:
        upload_test_product(
            name=t,
            description=text.text(quantity=2),
            price=generation_price(),
            qty=generation_qty(),
            category_id=3,
        )

    # Game consoles
    for c in consoles:
        upload_test_product(
            name=c,
            description=text.text(quantity=2),
            price=generation_price(),
            qty=generation_qty(),
            category_id=4,
        )

    # Refrigerators
    for r in refr:
        upload_test_product(
            name=r,
            description=text.text(quantity=2),
            price=generation_price(),
            qty=generation_qty(),
            category_id=5,
        )

    # Washing machines
    for w in wash:
        upload_test_product(
            name=w,
            description=text.text(quantity=2),
            price=generation_price(),
            qty=generation_qty(),
            category_id=6,
        )



if __name__ == '__main__':
    main()
