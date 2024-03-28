class Product:
    def __init__(
        self,
        name: str | None = None,
        price: int | float | None = None,
        product_code: str | None = None,
        url: str | None = None,
        ) -> None:
        self.name = name
        self.price = price
        self.product_code = product_code
        self.url = url
