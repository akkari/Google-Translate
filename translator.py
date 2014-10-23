#!/usr/bin/python
# -*- coding:utf-8 -*-
# Created on 2014/10/11

from Tkinter import *
import re
import urllib, urllib2
from pygame import mixer
from PIL import Image, ImageTk
import tempfile

class translator:
    language_code = {'检测语言': 'auto', '英语': 'en', '日语': 'ja', '中文(简体)': 'zh-CN', '中文(繁体)': 'zh-TW', '德语': 'de', '俄语': 'ru',
                    '法语': 'fr', '意大利语': 'it', '韩语': 'ko'}

    def __init__(self, parent):
        self.draw_layout(parent)

    def draw_layout(self, parent):
        option_list = ('检测语言', '英语', '日语', '中文(简体)', '中文(繁体)', '德语', '俄语', '法语', '意大利语', '韩语')
# Frames
        self.src_frame = Frame(parent)
        self.src_top_frame = Frame(self.src_frame)
        self.src_bottom_frame = Frame(self.src_frame)
        self.target_frame = Frame(parent)
        self.target_top_frame = Frame(self.target_frame)
        self.target_bottom_frame = Frame(self.target_frame)

# Widgets
        self.src_lang = StringVar()
        self.src_lang.set('检测语言') # default source language
        self.src_om = OptionMenu(self.src_top_frame, self.src_lang, *option_list)

        self.target_lang = StringVar()
        self.target_lang.set('中文(简体)') # default target language
        self.target_om = OptionMenu(self.target_top_frame, self.target_lang, *option_list[1:])

        self.input_box = Text(self.src_bottom_frame, width=50, wrap=WORD)
        self.output_box = Text(self.target_bottom_frame, relief=RIDGE, width=50, wrap=WORD, bg='grey')

        self.translate_button = Button(self.target_top_frame, text='翻译', command=self.translate, bg='#3369E8', fg='white')
        self.input_box.bind('<Control-Return>', self.translate)


        sound_icon = ImageTk.PhotoImage(Image.open('./icons/sound.png').resize((30,30)))
        self.pronounce_src_button = Button(self.src_top_frame, image=sound_icon, command=lambda : self.pronounce('src'))
        self.pronounce_target_button = Button(self.target_top_frame, image=sound_icon, command=lambda : self.pronounce('target'))
        self.pronounce_src_button.img = sound_icon # keep the reference for the icon image.

# Do the packing.
        self.src_frame.pack(side=LEFT, anchor=W, expand=YES, fill=BOTH)
        self.src_top_frame.pack(side=TOP, expand=NO, fill=X)
        self.src_bottom_frame.pack(side=TOP, expand=YES, fill=BOTH)
        self.target_frame.pack(side=LEFT, anchor=W, expand=YES, fill=BOTH)
        self.target_top_frame.pack(side=TOP, expand=NO, fill=X)
        self.target_bottom_frame.pack(side=TOP, expand=YES, fill=BOTH)

        self.src_om.pack(side=LEFT, anchor=W)
        self.pronounce_src_button.pack(side=LEFT)
        self.input_box.pack(side=TOP, expand=YES, fill=BOTH)
        self.target_om.pack(side=LEFT, anchor=W)
        self.translate_button.pack(side=LEFT, anchor=W)
        self.pronounce_target_button.pack(side=LEFT)
        self.output_box.pack(side=LEFT, expand=YES, fill=BOTH)

    def pronounce(self, what):
        ie = 'UTF-8'
        if what == 'src':
            tl = self.language_code[self.src_lang.get().encode('utf8')]
            whole_text = self.input_box.get('1.0', END).strip()
        elif what == 'target':
            tl = self.language_code[self.target_lang.get().encode('utf8')]
            whole_text = self.output_box.get('1.0', END).strip()

        # Split the original text into small chunks and make separate requests to Google.
        # All the returned mp3 files will be concatenated and then played.

        total_length = len(whole_text)
        max_chunk_length = 100
        total = total_length / max_chunk_length + 1 if total_length % max_chunk_length else total_length / max_chunk_length # total number of chunk

        temp_mp3 = tempfile.TemporaryFile(mode='r+')
        for i in xrange(total):
            if i == total - 1:
                q = whole_text.encode('utf8')
            else:
                q = whole_text[:max_chunk_length].encode('utf8')
                whole_text = whole_text[max_chunk_length:]
            data = {'ie': ie, 'tl': tl, 'q': q, 'total': total, 'idx': str(i)}
            data = urllib.urlencode(data)
            url = 'https://translate.google.cn/translate_tts'
            header = {'User-Agent': 'Mozilla/5.0'}

            req = urllib2.Request(url, data, header)
            temp_mp3.write(urllib2.urlopen(req).read())

        temp_mp3.seek(0)
        mixer.init()
        mixer.music.load(temp_mp3)
        mixer.music.play()

    def translate(self, event=None):
        if self.input_box.get('1.0', END).strip():
            html_received = self.get_html()
            result = self.parse_html(html_received)

            self.output_box.delete('1.0', END)
            self.output_box.insert('1.0', result)

    def parse_html(self, html):
        pattern = r";TRANSLATED_TEXT='([^']+)'"
        match = re.search(pattern, html)
        result = match.group(1)

        result = result.replace(r'\x3cbr\x3e', '\n')
        result = result.replace(r'\x26#39;', "'")

        return result

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

