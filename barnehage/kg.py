from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad, insert_soknad, commit_all, select_alle_barnehager, select_alle_soknader)
from kgcontroller import get_alle_kommuner, get_barnehage_statistikk

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' # nødvendig for session

@app.route('/statistikk', methods=['GET', 'POST'])
def statistikk():
    kommuner = get_alle_kommuner()
    if request.method == 'POST':
        valgt_kommune = request.form['kommune']
        plot_url, statistikk_data = get_barnehage_statistikk(valgt_kommune)
        return render_template('statistikk.html', kommuner=kommuner, plot_url=plot_url, statistikk=statistikk_data, valgt_kommune=valgt_kommune)
    return render_template('statistikk.html', kommuner=kommuner)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)

@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        sd = request.form
        print(sd)
        log = insert_soknad(form_to_object_soknad(sd))
        print(log)
        session['information'] = sd
        return redirect(url_for('svar')) #[1]
    else:
        return render_template('soknad.html')

def select_barnehage_instans(barnehage_id):
    information = select_alle_barnehager()
    for barnehage in information:
        if barnehage.barnehage_id == barnehage_id:
            return barnehage
    return None
    
@app.route('/svar')
def svar():
    information = session.get('information')

    if (information is not None):
        priorities = information.get('liste_over_barnehager_prioritert_5')
        barnehage_list = []
        test = ""
        message = ""
        
        if len(priorities) > 0:
            
            kgpr = priorities.split(',') # ['1','2']
         
            
            for kgid in kgpr:
                
                barnehage_instans = select_barnehage_instans(int(kgid))
                #if barnehage_instans == 1:
                #test = barnehage_instans
                if barnehage_instans is not None and barnehage_instans.barnehage_ledige_plasser != 0:
                    barnehage_list.append(barnehage_instans)
                    message = "TILBUD om plass"
                else:
                    barnehage_list.append(barnehage_instans)
                    test = "Avslag, ikke ledig plass på barnehage ID " + kgid
                    
                
        else:
            message = "AVSLAG, ingen ledige plasser på valgte barnehagene"
    else:
        message = "Information"
  

        
    return render_template('svar.html',
                           data=information,
                           kglist=barnehage_list,
                           message=message,
                           test=test)

@app.route('/commit')
def commit():
    commit_all()
    return render_template('commit.html')

@app.route('/soknader')
def soknader():
    soknader = select_alle_soknader()
    return render_template('soknader.html', soknader=soknader)
     


"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""
