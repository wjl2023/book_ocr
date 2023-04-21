class document:
    def __init__(self):
        self.titles = []
    
    def add_title(self, chapter_obj):
        self.titles.append(chapter_obj)

    def __json__(self):
        return {
            "titles": [title.__json__() for title in self.titles]
        }


class chapter:
    def __init__(self, title):
        self.paragraphs = []
        self.title = title

    def add_paragraph(self, type, text, page):
        paragraph = {}
        paragraph["type"] = type
        paragraph["text"] = text
        paragraph["page"] = page
        self.paragraphs.append(paragraph)
    
    def get_paragraphs(self):
        return self.paragraphs

    def __json__(self):
        return {
            "title": self.title,
            "paragraphs": self.get_paragraphs()
        }


class paragraph:
    def __init__(self):
        self.paragraphs = []
    
    def add_paragraph(self, id_count, paragraph_count, father, id_type, text, page):
        paragraph = {}
        paragraph["id"] = id_count
        paragraph["para_id"] = paragraph_count
        paragraph["father"] = father
        paragraph["type"] = id_type
        paragraph["text"] = text
        paragraph["page"] = page
        self.paragraphs.append(paragraph)