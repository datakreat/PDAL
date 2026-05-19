class PhysicsState:

    def __init__(self):

        self.explicit = {}
        self.derived = {}
        self.missing = []
        self.violations = []
        self.equations_used = []

    def add_explicit(self, name, value):
        self.explicit[name] = value

    def add_derived(self, name, value):
        self.derived[name] = value

    def get(self, name):

        if name in self.explicit:
            return self.explicit[name]

        return self.derived.get(name)

    def has(self, name):
        return self.get(name) is not None