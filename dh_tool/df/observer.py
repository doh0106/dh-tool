class Observer:
    def update(self, dataframe):
        pass


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, dataframe):
        for observer in self._observers:
            observer.update(dataframe)
