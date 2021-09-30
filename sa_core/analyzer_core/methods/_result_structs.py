# Results of Chi-Square method struct
class ChiSqrRes:
    fullness = None
    visualized = None

    def __init__(self, fullness, visualized):
        self.fullness = fullness
        self.visualized = visualized


# Results of Regular-Singular method struct
class RsRes:
    volume = None

    def __init__(self, volume):
        self.volume = volume


# Results of Koch-Zhao Analysis method struct
class KzaRes:
    threshold = None
    indexes = None
    volume = None
    data = None

    def __init__(self, threshold, indexes, volume, data):
        self.threshold = threshold
        self.indexes = indexes
        self.volume = volume
        self.data = data
