#!/usr/bin/python
# -*- coding:utf-8 -*-
# Created on 2014/10/11

from Tkinter import *
import re
import urllib, urllib2

class translator:
    language_code = {'检测语言': 'auto', '英语': 'en', '日语': 'ja', '中文(简体)': 'zh-CN', '中文(繁体)': 'zh-TW', '德语': 'de', '俄语': 'ru',
                    '法语': 'fr', '意大利语': 'it', '韩语': 'ko'}
    def __init__(self, parent):
        self.draw_layout(parent)

    def draw_layout(self, parent):
        option_list = ('检测语言', '英语', '日语', '中文(简体)', '中文(繁体)', '德语', '俄语', '法语', '意大利语', '韩语')
#        self.src_frame = Frame(parent)
#        self.target_frame = Frame(parent)
#        self.src_frame.pack(side=LEFT, anchor=W, expand=YES, fill=BOTH)
#        self.target_frame.pack(side=LEFT, anchor=W, expand=YES, fill=BOTH)
        for x in xrange(2):
            parent.grid_rowconfigure(x, weight=1)
        for y in xrange(4):
            parent.grid_columnconfigure(y, weight=1)

        self.src_lang = StringVar()
        self.src_lang.set('检测语言') # default source language
        self.src_om = OptionMenu(parent, self.src_lang, *option_list)

        self.target_lang = StringVar()
        self.target_lang.set('中文(简体)') # default target language
        self.target_om = OptionMenu(parent, self.target_lang, *option_list[1:])

        self.input_box = Text(parent)
        self.result = StringVar()
        self.output_box = Label(parent, textvariable=self.result, relief=RIDGE, width=50)

        self.translate_button = Button(parent, text='翻译', command=self.translate, bg='#3369E8', fg='white')
        self.input_box.bind('<Control-Return>', self.translate)


        self.src_om.grid(row=0, column=0, sticky=W)
        self.target_om.grid(row=0, column=2, sticky=W)
        self.translate_button.grid(row=0, column=3, sticky=W)
        self.input_box.grid(row=1, column=0, sticky=W+E+S+N)
        self.output_box.grid(row=1, column=2, columnspan=2, sticky=W+E+S+N)

    def translate(self, event=None):
        if self.input_box.get('1.0', END).strip():
            html_received = self.get_html()
            result = self.parse_html(html_received)
            self.result.set(urllib.unquote(result))

    def parse_html(self, html):
        pattern = r";TRANSLATED_TEXT='([^']+)'"
        match = re.search(pattern, html)
        result = match.group(1)
        return result.replace(r'\x3cbr\x3e', '\n')

    def get_html(self):
        ie = 'UTF-8'
        langpair = '%s|%s' % (self.language_code[self.src_lang.get().encode('utf8')], self.language_code[self.target_lang.get().encode('utf8')])
        text = self.input_box.get('1.0', END).rstrip().encode('utf8')
        hl = 'zh-CN'
        values = {'hl':hl, 'ie':ie, 'text':text, 'langpair':langpair}
        data = urllib.urlencode(values)
        url = 'http://translate.google.cn'
        header = {'User-Agent': 'Mozilla/5.0'}

        req = urllib2.Request(url, data, header)
        response = urllib2.urlopen(req)
        result = response.read()
        with open('result.html', 'w') as f:
            f.write(result)

        return result

def main():
    root = Tk()
    root.title('Google Translate')
    t = translator(root)
    root.mainloop()


if __name__=="__main__":main()

