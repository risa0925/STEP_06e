#!/usr/bin/env python
# coding: utf-8
import webapp2

form_HTML = """
    <form action="/output" method="post">
        <input type="text" name="a"><br>
        <input type="text" name="b"><br>
        <input type="submit">
    </form>"""

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.write('<title>乗り換え案内</title>')
        self.response.write(form_HTML)

class outputPage(webapp2.RequestHandler):
    def post(self):
        a_list = list(self.request.get('a'))
        b_list = list(self.request.get('b'))
        output_list = []

        for i in range(len(a_list)):
            output_list.append(a_list[i])
            output_list.append(b_list[i])
        outputWord = "".join(output_list)

        self.response.write(outputWord)
        self.response.write(form_HTML)

app = webapp2.WSGIApplication([('/', MainPage),('/output',outputPage)], debug=True)
