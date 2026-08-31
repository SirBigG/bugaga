import re


class UkrainianStemmer:
    def __init__(self, word):
        self.word = word
        self.perfectiveground = r"(ив|ивши|ившись|ыв|ывши|ывшись((?<=[ая])(в|вши|вшись)))$"
        self.reflexive = r"(с[яьи])$"
        self.adjective = r"(ими|ій|ий|а|е|ова|ове|ів|є|їй|єє|еє|я|ім|ем|им|ім|их|іх|ою|йми|іми|у|ю|ого|ому|ої)$"
        self.participle = r"(ий|ого|ому|им|ім|а|ій|у|ою|ій|і|их|йми|их)$"
        self.verb = r"(сь|ся|ив|ать|ять|у|ю|ав|али|учи|ячи|вши|ши|е|ме|ати|яти|є)$"
        self.noun = (
            r"(а|ев|ов|е|ями|ами|еи|и|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|"
            r"ия|ья|я|і|ові|ї|ею|єю|ою|є|еві|ем|єм|ів|їв|ю)$"
        )
        self.rvre = r"[аеиоуюяіїє]"
        self.derivational = r"[^аеиоуюяіїє][аеиоуюяіїє]+[^аеиоуюяіїє]+[аеиоуюяіїє].*(?<=о)сть?$"
        self.rv = ""

    def _sub(self, value, expression, replacement):
        original = value
        self.rv = re.sub(expression, replacement, value)
        return original != self.rv

    def stem_word(self):
        word = self.word.lower().replace("'", "").replace("ё", "е").replace("ъ", "ї").replace("ы", "и")
        match = re.search(self.rvre, word)
        if not match:
            return word
        start = word[: match.span()[1]]
        self.rv = word[match.span()[1] :]
        if not self._sub(self.rv, self.perfectiveground, ""):
            self._sub(self.rv, self.reflexive, "")
            if self._sub(self.rv, self.adjective, ""):
                self._sub(self.rv, self.participle, "")
            elif not self._sub(self.rv, self.verb, ""):
                self._sub(self.rv, self.noun, "")
        self._sub(self.rv, r"и$", "")
        if re.search(self.derivational, self.rv):
            self._sub(self.rv, r"ость$", "")
        if self._sub(self.rv, r"ь$", ""):
            self._sub(self.rv, r"ейше?$", "")
            self._sub(self.rv, r"нн$", "н")
        return start + self.rv
