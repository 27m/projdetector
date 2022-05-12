class Detector:

    def __init__(self, items, config):
        self.config = config
        self.items = items

    def detect(self):
        items = self.items
        print("a")


def main():
    detector = Detector("items_go_here", "config_goes_here")
    detector.detect()


if __name__ == "__main__":
    main()