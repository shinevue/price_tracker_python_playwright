class Product:
    def __init__(
            self,
            name: str | None = None,
            price: int | None = None
        ) -> None:
        self.name = name
        self.price = price
