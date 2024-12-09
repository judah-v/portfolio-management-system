import os
import tkinter as tk
import webbrowser as wb
import mysql.connector as mc
import qrcode as qr
import threading

from tkinter import messagebox as mb
from flask import Flask, render_template
from signal import CTRL_C_EVENT


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '.yearup1298B', 
    'database': 'portfolio_management'}

DEPLOY_PATH = os.path.dirname(os.path.abspath(__file__))

flask_app = Flask(__name__)

class App:
    def __init__(self):
        self.conn = mc.connect(**DB_CONFIG)
        self.dbc = self.conn.cursor(dictionary=True)
        self.current_pages = []
        self.home = MainPage(self, 'Manage Portfolio', [500,500])
        self.start_server()
        self.home.win.protocol('WM_DELETE_WINDOW', self.stop_server)

    def get_data(self):
        query = "select author_name as 'name', project_name as 'title', author_bio as bio, project_desc as 'desc', project_link as link from authors join projects on authors.author_id = projects.author_id"
        self.dbc.execute(query)
        results = self.dbc.fetchall()
        return results[0] if results else None

    def generate_qr_images(self):
        self.dbc.execute('select project_name as "name", project_link as link from projects')
        links = self.dbc.fetchall()
        for link in links:
            if link['link']:
                img = qr.make(link['link'])
                img.save(f'{DEPLOY_PATH}/static/images/{link['name'].replace(' ', '_')}.png')
    
    def start_server(self, debug=False):
        self.server_thread = threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', debug=debug))
        self.server_thread.start()

    def stop_server(self):
        os.kill(CTRL_C_EVENT, 1)

    def run(self):
        self.home.win.mainloop()

    def restart(self):
        self.home.close()
        self.__init__()


class Page:
    def __init__(self, app, title, size=[500,500]):
        self.app = app
        for page in app.current_pages:
            if type(self) == type(page):
                page.win.deiconify()
                return
        win = tk.Tk()
        win.minsize(*size)
        win.title(title)
        self.win = win
        self.app.current_pages.append(self)
        self.win.protocol('WM_DELETE_WINDOW', self.close)
        self.win.focus_force()

    def next_field(self, e):
        if e.char == '\r':
            keys = list(self.input_boxes.keys()) # Get names of input boxes
            inputs = [self.input_boxes[key] for key in keys] # Get a list of input widgets in the same order as keys
            next_index = inputs.index(e.widget) + 1
            self.input_boxes[keys[next_index]].focus()

    def close(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass
        self.app.current_pages.remove(self)
        open_pages = self.app.current_pages.copy()
        if type(self) == MainPage:
            for page in open_pages:
                page.close()
    
    def save_data(self, data):
        ... # To be implemented individually


class MainPage(Page):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manage_btn = tk.Button(self.win, text="Add Project", command=self.start_project_page)
        self.add_info_btn = tk.Button(self.win, text="Edit Personal Information", command=self.start_addinfo_page)
        self.deploy_btn = tk.Button(self.win, text="Preview Page", command=lambda: wb.open("http://127.0.0.1:5000/", 2))
        self.proj_lbl = tk.Label(self.win, text="Projects", font=("Arial", 20, 'bold'))
        self.title_lbl = tk.Label(self.win, text="Portfolio", font=("Arial", 20, 'bold'))

        projects = self.get_projects()
        self.title_lbl.pack(pady=10)
        for btn in [self.manage_btn, self.add_info_btn, self.deploy_btn]:
            btn.pack(pady=5)

        self.proj_lbl.pack(pady=25)
        self.proj_frame = tk.Frame(self.win)
        for project in projects:
            lbl = tk.Label(self.proj_frame, text=project[1].title())
            btn = tk.Button(self.proj_frame, text="Remove", command=lambda: self.delete_project(project[0]))
            row = projects.index(project) + 1
            lbl.grid(column=1, row=row, pady=5)
            btn.grid(column=2, row=row)

        self.proj_frame.pack()

    def get_projects(self):
        self.app.dbc.execute("select project_id as id, project_name as 'name' from projects")
        proj_dict = self.app.dbc.fetchall()
        projects = []
        for proj in proj_dict: 
            projects.append([proj['id'], proj['name']])
        return projects
    
    def delete_project(self, id):
        if mb.askokcancel('Delete Project', 'Are you sure you want to delete this project from the database?'):
            self.app.dbc.execute(f'select project_name as "name" from projects where project_id = {id}')
            link = self.app.dbc.fetchone()
            try:
                os.remove(f'{DEPLOY_PATH}/static/images/{link['name'].replace(' ', '_')}.png') # delete any generated images
            except FileNotFoundError:
                pass
            self.app.dbc.execute(f'delete from projects where project_id = {id}')
            self.app.conn.commit()
            self.app.restart()

    def start_addinfo_page(self):
        page = AddInfoPage(self.app, 'Add Personal Information')

    def start_project_page(self):
        page = AddProjectPage(self.app, 'Add Project')
    

class AddInfoPage(Page):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for page in self.app.current_pages:
            if type(self) == type(page) and page != self:
                return
        
        self.name_label = tk.Label(self.win, text="Name")
        self.name_box = tk.Entry(self.win, width=30)
        self.bio_label = tk.Label(self.win, text="Biography")
        self.bio_box = tk.Text(self.win, height=10, width=30)
        self.submit_btn = tk.Button(self.win, text="Save", command=self.submit_data)
        data = self.app.get_data()
        if not data:
            self.app.dbc.execute('insert into authors values (1, "your name", "your biography")')
            self.app.conn.commit()
            data = self.app.get_data()

        self.name_box.bind('<Key>', self.next_field)
        

        self.input_boxes = {'name': self.name_box, 'bio': self.bio_box}
        if data:
            self.name_box.insert(0, data['name'])
            self.bio_box.insert('1.0',data['bio'] )
        for element in [self.name_label, self.name_box, self.bio_label, self.bio_box, self.submit_btn]:
            element.pack()
        
    def submit_data(self):
        if not self.name_box.get():
            mb.showwarning('Invalid submission', 'Please insert a name')
            self.win.focus_force()
        else:
            data = {
                'name': self.name_box.get(),
                'bio': self.bio_box.get('1.0', 'end-1c').replace("'", "\\'").replace('"', '\\"')
            }
            self.save_data(data)
            self.app.restart()

    def save_data(self, data):
        for field in data:
            query = f"update authors set author_{field} = '{data[field]}' where author_id = 1"
            self.app.dbc.execute(query)
            self.app.conn.commit()


class AddProjectPage(Page):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for page in self.app.current_pages:
            if type(self) == type(page) and page != self:
                return
        self.name_label = tk.Label(self.win, text="Name")
        self.name_box = tk.Entry(self.win, width=30)
        self.desc_label = tk.Label(self.win, text="Description")
        self.desc_box = tk.Text(self.win, height=10, width=25)
        self.link_label = tk.Label(self.win, text="Link")
        self.link_box = tk.Entry(self.win, width=30)
        self.submit_btn = tk.Button(self.win, text="Save", command=self.submit_data)

        self.name_box.bind('<Key>', self.next_field)
        self.link_box.bind('<Key>', self.next_field)
        
        self.input_boxes = {
            'name': self.name_box, 
            'link': self.link_box, 
            'desc': self.desc_box}
        all_elements = [
            self.name_label, 
            self.name_box, 
            self.link_label, 
            self.link_box, 
            self.desc_label, 
            self.desc_box, 
            self.submit_btn]

        for element in all_elements:
            element.pack()
          
    def submit_data(self):
        if not self.name_box.get():
            mb.showwarning('Invalid submission', 'Please insert a name')
            self.win.focus_force()
        else:
            data = {
                'name': self.name_box.get(), 
                'link': self.link_box.get(),
                'desc': self.desc_box.get('1.0', 'end-1c')}

            self.save_data(data)
            self.app.restart()
            
    def save_data(self, data):
        keys = data.keys()
        fieldnames = "("+ ', '.join(['project_'+key for key in keys]) + ", author_id)"
        query = f"insert into projects {fieldnames} values {tuple([data[key] for key in keys]+[1,])}"
        self.app.dbc.execute(query)
        self.app.conn.commit()
        self.app.generate_qr_images()



@flask_app.route('/')
def index():
    c = app.conn.cursor(dictionary=True)
    c.execute('select author_name as "name", author_bio as bio from authors')
    author = c.fetchone()
    c.execute('select project_name as "name", project_desc as "desc", project_link as link from projects')
    projects = c.fetchall()
    for project in projects:
        path = f'/images/{project['name'].replace(' ', '_')}.png'
        if project['link']:
            project['img'] = path

    return render_template(f'index.html', author=author, projects=projects)

if __name__ == '__main__':
    app = App()
    app.run()
    app.conn.close()