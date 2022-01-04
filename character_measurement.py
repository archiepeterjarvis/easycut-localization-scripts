# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
import string
import pyodbc

kv = '''
<MeasureCharacters>
    measurement_label: measurement_label

    Label: 
        id: measurement_label
        text: 'a'
        font_size: 20
        size: self.texture_size
        size_hint: (None, None)'''

Builder.load_string(kv)

class Database(object):
    def __init__(self):
        #ask for credentials
        self.server = ''
        self.database = ''
        self.username = ''
        self.password = ''
        self.cnn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password + ';')
        self.cursor = self.cnn.cursor()

    def input_character(self, character, font_size, width):
        sql = "INSERT INTO Characters (Letter, FontSize, Width) VALUES (?, ?, ?)"

        params = (character.decode('utf-8'), font_size, width)

        self.cursor.execute(sql, params)
        self.cnn.commit()


class MeasureCharacters(Screen):
    def __init__(self, **kwargs):
        super(MeasureCharacters, self).__init__(**kwargs)
        self.database = Database()

        self.char = 0
        self.font_size = 12
        self.char_width = {

        }
        accent_list = [".", ",", " ", "!", "?", "¡", "¿", "Ä", "ä", "À", "à", "Á", "á", "Â", "â", "Ã", "ã", "Å", "å", "Ǎ", "ǎ", "Ą", "ą", "Ă", "ă", "Æ", "æ", "Ā", "ā", "Ç", "ç", "Ć", "ć", "Ĉ", "ĉ", "Č", "č", "Ď", "đ", "Đ", "ď", "ð", "È", "è", "É", "é", "Ê", "ê", "Ë", "ë", "Ě", "ě", "Ę", "ę", "Ė", "ė", "Ē", "ē", "Ĝ", "ĝ", "Ģ", "ģ", "Ğ", "ğ", "Ĥ", "ĥ", "Ì", "ì", "Í", "í", "Î", "î", "Ï", "ï", "ı", "Ī", "ī", "Į", "į", "Ĵ", "ĵ", "Ķ", "ķ", "Ĺ", "ĺ", "Ļ", "ļ", "Ł", "ł", "Ľ", "ľ", "Ŀ", "ŀ", "Ñ", "ñ", "Ń", "ń", "Ň", "ň", "Ņ", "ņ", "Ö", "ö", "Ò", "ò", "Ó", "ó", "Ô", "ô", "Õ", "õ", "Ő", "ő", "Ø", "ø", "Œ", "œ", "Ŕ", "ŕ", "Ř", "ř", "ẞ", "ß", "Ś", "ś", "Ŝ", "ŝ", "Ş", "ş", "Š", "š", "Ș", "ș", "Ť", "ť", "Ţ", "ţ", "Þ", "þ", "Ț", "ț", "Ü", "ü", "Ù", "ù", "Ú", "ú", "Û", "û", "Ű", "ű", "Ũ", "ũ", "Ų", "ų", "Ů", "ů", "Ū", "ū", "Ŵ", "ŵ", "Ý", "ý", "Ÿ", "ÿ", "Ŷ", "ŷ", "Ź", "ź", "Ž", "ž", "Ż", "ż"]
        plain_list = [char for char in string.ascii_letters]
        self.char_list = accent_list + plain_list

    def on_enter(self):
        Clock.schedule_interval(self.get_label_size, 0)

    #measure with different font size
    #enter into database

    def get_label_size(self, dt):
        label = self.ids.measurement_label
        label.font_size = self.font_size
        label.text = self.char_list[self.char]
        width = label.width

        if len(self.char_list) == self.char + 1:
            if self.font_size < 40:
                self.char = 0
                self.font_size += 2
            else:
                Clock.unschedule(self.get_label_size)
        else:
            self.char += 1

            print(self.font_size)

            self.database.input_character(label.text, self.font_size, width)
