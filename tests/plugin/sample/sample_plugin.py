from main import GeneratorBase


class SamplePlugin(GeneratorBase):
    def __init__(self, value, fmt):
        self.value = value
        self.fmt = fmt

    def get(self):
        return self.fmt.get().format(self.value.get())

    def update(self):
        self.fmt.update()
        self.value.update()
