# required to resolve in eval
from kivy.properties import StringProperty, ObjectProperty

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner

# required for google sheets
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

import itertools


#template object for storing labels found
class LabelTemplate(object):
    def __init__(self, screen, id, height, width, line_height, font_size):
        self.screen = screen
        self.id = id
        self.height = height
        self.width = width
        self.line_height = line_height
        self.font_size = font_size

class Scraper(object):
    def __init__(self, a, l, set, sm, m):
        self.a = a
        self.l = l
        self.set = set
        self.sm = sm
        self.m = m

        #set up gsheets
        self.sheet_id = '1ioz_Y6z5P-Z5PusXsKnPk4j1zGGR3pUizpcPiOd5kDo'
        self.sample_range = 'Strings!A2:G'
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']

    #check whether text can be evaluated in python
    def is_valid(self, text):
        try:
            exec(text)
            return True
        except:
            return False

    #get all lines from a text file
    def get_text(self, file):
        with open(file) as f:
            return f.readlines()

    #get the lines where text the correct pattern is found (' = ')
    def get_lines(self, file):
        text = self.get_text(file)

        lines = []

        buffer = ''

        for line in text:
            line_split = line.split(' = ')
            if len(line_split) == 2:
                name_split = line_split[0].split('.')
                if len(name_split) == 3:
                    if name_split[2] == 'text':
                        if self.is_valid(' '.join(line.split())):
                            lines.append(' '.join(line.split()))
                        else:
                            if buffer == '':
                                buffer += ' '.join(line.split())
                            else:
                                if self.is_valid(buffer.strip() + ' '.join(line.split())):
                                    lines.append(buffer.strip() + ' '.join(line.split()))
                                    buffer = ''
                                else:
                                    buffer += ' '.join(line.split())
        return lines

    #try to piece together a variable declaration over multiple lines by evaluating with is_valid() until True
    def get_variable_value(self, file):
        lines = self.get_text(file)

        buffer = ''

        new_lines = []

        for line in lines:
            if self.is_valid(line) and buffer == '':
                new_lines.append(''.join(s for s in line if ord(s)>31 and ord(s)<126))
            else:
                if self.is_valid(buffer + line):
                    new_lines.append(''.join(s for s in buffer if ord(s)>31 and ord(s)<126) + ''.join(s for s in line if ord(s)>31 and ord(s)<126))
                    buffer = ''
                else:
                    buffer += line

        return new_lines

    def run(self):
        lines = self.get_lines('C:\\Users\\Archie\\Documents\\easycut\\easycut-smartbench\\src\\asmcnc\\skavaUI\\screen_go.py')

        print(lines)

    #export data to spreadsheet
    def export_to_spreadsheet(self, variables):
        values = []

        print(variables)

        for var in variables:
            variable_name = var[0]
            variable_value = var[1]

            obj = self.get_label_from_name(variable_name)

            if obj != None:
                values.append([obj.screen, obj.id, variable_value, obj.width, obj.height, obj.line_height, obj.font_size])

        #sort and remove duplicates
        values.sort()
        values = list(value for value, _ in itertools.groupby(values))

        body = {
            'values': values
        }

        creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=self.scope)

        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()

        result = sheet.values().append(spreadsheetId=self.sheet_id, range=self.sample_range, valueInputOption='RAW', body=body).execute()

        print('{0} cells appended.'.format(result \
                                       .get('updates') \
                                       .get('updatedCells')))
