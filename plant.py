class Plant:
    def __init__(self) -> None:
        self.wilt: bool = False
        self.state: int = 0


class Bot:

    def __init__(self) -> None:
        self.plants: dict[str, Plant] = {'timeenjoyed': Plant(), 'mystypy': Plant()}  # Sample data filled here...

        # To get JSON of all Plants...
        json = {k: vars(v) for k, v in self.plants.items()}
        print(json)


Bot()