#!/usr/bin/python
# -*- coding: utf-8 -*-
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1

from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Template
htmltag = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Restaurant Info</title>\
            <link rel="stylesheet" href="https://bootswatch.com/darkly/bootstrap.min.css">\
            <style>.navbar-header, .sub{float: left;padding: 21px;text-align: center;width: 100%;\
            }.navbar-brand {float:none;} h1{text-align: center;}</style></style></head><body>'
navBar = '<nav class="navbar navbar-default"><div class="container">\
                    <div class="navbar-header"><a class="navbar-brand" href="index.html">Restaurant Info</a>\
                    </div></div></nav>'           


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Objective 3 Step 2 - Create /restarants/new page
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ''
                output += htmltag+navBar 
                output += "<h1>Create a New Restaurant</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
                output += "<input name = 'newRestaurantName' class='form-control' type = 'text' placeholder = 'New Restaurant Name' > "
                output += "</br></br><input type='submit' class='btn btn-primary' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ''
                    output += htmltag+navBar 
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantIDPath
                    output += "<input name = 'newRestaurantName' class='form-control' \
                    type='text' placeholder = '%s' >" % myRestaurantQuery.name
                    output += "</br><input type = 'submit' class='btn btn-primary' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"  
                    self.wfile.write(output)  

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += htmltag+navBar 
                    output += "<h1>Are you sure you want to delete %s?" % myRestaurantQuery.name
                    output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantIDPath
                    output += "</br><input type = 'submit' class='btn btn-primary' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)

            if self.path.endswith('/restaurants'):
                restaurants = session.query(Restaurant).all()
                output = ''
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # output += "<html><body>"

                output += '<!DOCTYPE html>'
                output += htmltag+navBar
                # Objective 3 Step 1 - Create a Link to create a new menu item
                output += "<a class='sub' href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"    
                for restaurant in restaurants:
                    output += '<div class="col-md-3 movie-result">';
                    output +=   '<div class="well text-center">';
                    output += restaurant.name
                    output += '</br>'
                    # Objective 2 -- Add Edit and Delete Links
                    output += "<a href ='/restaurants/%s/edit' >Edit</a>" % restaurant.id
                    output += "</br>"
                    output += "<a href ='/restaurants/%s/delete'> Delete </a>" % restaurant.id
                    output +=   '</div>';
                    output += '</div>';
                output += '</body></html>'
                self.wfile.write(output)
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

        # Objective 3 Step 3- Make POST method
    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery:
                    session.delete(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery = session.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    # Create new Restaurant Object
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()    

        except:
            pass            

def main():
    try:
        server = HTTPServer(('', 8080), webServerHandler)
        print 'Web server running...open localhost:8080/restaurants in your browser'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()


if __name__ == '__main__':
    main()
