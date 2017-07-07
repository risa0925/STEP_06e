#!/usr/bin/env python
# coding: utf-8
import webapp2
import json
import urllib2

jsonURL = 'http://tokyo.fantasy-transit.appspot.com/net?format=json'
jsonData = json.load(urllib2.urlopen(jsonURL))

title_HTML = """<title>乗り換え案内</title>
<h1>乗り換え案内</h1>
"""


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.write(title_HTML)
        self.response.write("""<form action="/transferGuide" method="post">
        出発駅：<select name="departure">""")

        # display departure stations
        for route in jsonData:
            self.response.write('<option disabled>--%s--</option>' % route['Name'])
            for station in route['Stations']:
                self.response.write('<option>%s</option>' % station)
        self.response.write('</select><br>')

        # display arrival stations
        self.response.write('到着駅：<select name="arrival">')
        for route in jsonData:
            self.response.write('<option disabled>--%s--</option>' % route['Name'])
            for station in route['Stations']:
                self.response.write('<option>%s</option>' % station)
        self.response.write("""</select><br>
        <input type="submit" value="検索"></form>""")


class transferGuide(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.write(title_HTML)
        start = self.request.get('departure')
        end = self.request.get('arrival')
        # display
        self.response.write('Departure station = %s ' % start)
        self.response.write('<br>  Arrival Station = %s' % end)

        self.plan(start, end)

    def plan(self, start, end):
        next_line = self.recommend_line(start, end)
        route = []
        transfer_station = {}

        for index in range(1, len(next_line)):
            transfer = self.get_intersection_station(next_line[index - 1], next_line[index])
            transfer_station[(next_line[index - 1], next_line[index])] = transfer
            route.append(transfer[0])
        if len(transfer_station) != 0:
            self.response.write('<br>乗り換え駅(s): ')
            for station in route:
                self.response.write('<b style="color:chocolate"> %s </b>' % station)
                if station != route[len(route) - 1]:
                    self.response.write('and')
            self.response.write('<hr><br>')

            route.insert(0, start)
            route.append(end)
            for i in range(0, len(route) - 1):
                if i != 0:
                    self.response.write('<b style="color:orange">Transfer to >> </b>')
                self.print_route(route[i], route[i + 1])

    def recommend_line(self, start, end):  # return a list of recommend lines
        start_line = self.get_line(start) #eg.yamanote-line
        end_line = self.get_line(end) #eg.chuo-line
        count = 0
        route_line = []
        rec_line = []

        while not self.check_in_line(start_line, end):
            route_line.append(start_line)
            next_lines = set()
            for line in start_line:
                next_lines |= self.transferable_line(line)
            start_line = next_lines
            count += 1

        last_line = ''
        for line in (end_lines & start_line):
            last_line = line
        rec_line.append(last_line)

        for line_set in route_line[::-1]:
            for line in (line_set & self.transferable_line(last_line)):
                last_line = line
            rec_line.append(line)

        rec_line.reverse()
        if count != 0:
            self.response.write('<br><hr>乗り換え回数: %d 回' % count)

        return rec_line


    def get_line(self, target_station):  # get the line of target station 
        line = set()
        for dictionary in jsonData:
            for station in dictionary['Stations']:
                # build set of station and line
                if station == target_station:
                    line.add(dictionary['Name']) #What line eg Yamanote-line
        return line

    def check_in_line(self, start_line, target):  # check if the station is in current lines
        for line in start_line:
            if target in self.get_whole_line(line)['Stations']:
                return True
        return False


    def get_whole_line(self, line):  # get the whole dictionary of the line
        for dictionary in jsonData:
            if dictionary['Name'] == line:
                return dictionary

    def get_index(self, target, list):
        for index in range(len(list)):
            if list[index] == target:
                return index

    def get_station_num(self, line):
        return len(self.get_whole_line(line)['Stations'])

    def check_same_line(self, start, end):  # check if the two stations are in the same line
        start_line = self.get_line(start)
        end_line = self.get_line(end)
        for line in start_line:
            if line in end_line:
                return True
        return False



    def get_intersection_station(self, a, b):
        line_a = set()
        line_b = set()
        for station in self.get_whole_line(a)['Stations']:
            line_a.add(station)
        for station in self.get_whole_line(b)['Stations']:
            line_b.add(station)
        intersection_station = [i for i in (line_a & line_b)]
        return intersection_station

    def transferable_line(self, line):  # return set of lines can be transferred through the given line
        line_set = set()
        for station in self.get_whole_line(line)['Stations']:
            for line in self.get_line(station):
                line_set.add(line)
        return line_set



    def print_route(self, start, end):
        intersection_line = (self.get_line(start) & self.get_line(end))
        for line in intersection_line:
            self.response.write('<b style="color:orange">[ %s: ' % self.get_whole_line(line)['Name'])
            start_index = self.get_index(start, self.get_whole_line(line)['Stations'])
            end_index = self.get_index(end, self.get_whole_line(line)['Stations'])
            if start_index < end_index:
                if (end_index - start_index) > (self.get_station_num(line) / 2):
                    route = self.get_whole_line(line)['Stations'][end_index:]
                    for i in range(1, start_index + 1):
                        route.append(self.get_whole_line(line)['Stations'][i])
                    route.reverse()
                    self.response.write('up ]')
                else:
                    route = self.get_whole_line(line)['Stations'][start_index:end_index + 1]
                    self.response.write('down ]')
            else:
                if (start_index - end_index) > (self.get_station_num(line) / 2):
                    route = self.get_whole_line(line)['Stations'][start_index:]
                    for i in range(1, end_index + 1):
                        route.append(self.get_whole_line(line)['Stations'][i])
                    self.response.write('down ]')
                else:
                    route = self.get_whole_line(line)['Stations'][end_index:start_index + 1]
                    route.reverse()
                    self.response.write('up ]')

            self.response.write('</b><br>')
            for station in route:
                if station == route[0] or station == route[len(route) - 1]:
                    self.response.write('>> <b style="color:cornflowerblue">%s</b><br>' % station)
                else:
                    self.response.write('>> %s<br>' % station)




app = webapp2.WSGIApplication([('/', MainPage), ('/transferGuide', transferGuide)], debug=True)
