class User:
    def __init__(self, id, name, phone, lang, session: str = ''):
        self.id = id
        self.name = name
        self.phone = phone
        self.lang = lang
        self.session = session

    def __repr__(self):
        return f'User(id={self.id}, name={self.name}, phone={self.phone}, lang={self.lang}, session=***)'

    def __str__(self):
        return f'{{{self.id}, {self.name}, {self.phone}, {self.lang}, ***}}'
