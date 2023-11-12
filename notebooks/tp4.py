#!usr/bin/python3
#-*-coding: utf-8-*-

import sqlite3
from flask import Flask
from logging import debug
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

app = Flask(__name__)

##################
### TP4
##################

@app.route("/hello") # creation de la route hello
def hello():
    return "hello world"

# Launch at startup
## DEV: explore SQL interface
# Load SQL DUMP
# CREATE SQL REQUEST (STR)
# CONNECT AND FETCH
# PRINT(FETCH_RESULT)

@app.route("/")
def root():

    # Create a connection object that represent the database
    con = sqlite3.connect("ensembl_hs63_simple.sqlite")

    # Create a cursor object
    cur = con.cursor()

    # CREATE SQL REQUEST (STR) and call cur's execute() method to perform SQL commands
    my_request = """SELECT DISTINCT Atlas_Organism_Part
    FROM Expression
    WHERE atlas_organism_part IS NOT NULL
    ORDER BY atlas_organism_part"""
    cur.execute(my_request)
    atlas_organism_part = cur.fetchall() # permet de récupérer d'un coup l'ensemble des résultats d'une requête
    atlas_organism_sort = sorted([_[0] for _ in atlas_organism_part if _[0]])
    print(cur.fetchone()) # ce qui s'affiche dans le shell
    con.commit() # uniquement si on insère qqch dans la table
    con.close()

    return render_template('atlas_part_org.html', atlas_value=atlas_organism_sort)
    # le render_template() permet de générer la page HTML qui sera affichée dans le navigateur à partir du template
    # atlas_part_org.html est de la valeur atlas_value, assignée à atlas_org_part_sort

    return str(atlas_org_part_sort) # STR: affichée dans la page HTML

@app.route("/parts/<part>/genes") # <part> => à mettre ds les paramètres de la fonction
def part_gene_info(part):
    con2 = sqlite3.connect("ensembl_hs63_simple.sqlite")
    cur2 = con2.cursor()
    my_request2 = f"""SELECT DISTINCT g.ensembl_gene_id, associated_gene_name
    FROM Genes as g
    NATURAL JOIN Transcripts as t
    NATURAL JOIN Expression as e
    WHERE atlas_organism_part = "{part}"
    ORDER BY g.ensembl_gene_id"""
    cur2.execute(my_request2)
    liste_genes = cur2.fetchall() 
    l = [] # pour chaque ligne, on ajoute dans l tous les gènes d'un atlas_organism_part
    for row in liste_genes: # regarde tous les fetchall()
        l.append(row)
    return render_template('gene_info_parts.html', gene_info=l) 
    return f"<h2>{part}</h2>"

# tester en tapant la route avec part = adipose%20tissue (pour faire les espaces: %20)

@app.route("/genes/<id>")
def gene_card(id):
    con3 = sqlite3.connect("ensembl_hs63_simple.sqlite")
    cur3 = con3.cursor()

    # une section présentant toutes les infos données par ligne correspondante de la table Genes pour 1 seul gène
    my_request3 = f"""SELECT DISTINCT g.ensembl_gene_id, chromosome_name, band, strand, gene_start, gene_end, associated_gene_name, transcript_count
    FROM Genes as g
    NATURAL JOIN Transcripts as t
    WHERE ensembl_gene_id = "{id}"
    """
    cur3.execute(my_request3)
    res=cur3.fetchall()

    # une section présentant la liste des transcrits de ce gène (avec leur identifiant et leurs positions de début et de fin)
    con4 = sqlite3.connect("ensembl_hs63_simple.sqlite")
    cur4 = con4.cursor()
    my_request4 = f"""SELECT DISTINCT t.Ensembl_Transcript_ID, t.Ensembl_Gene_ID, t.Transcript_Start, t.Transcript_End
    FROM Transcripts as t
    WHERE t.ensembl_gene_id = "{id}"
    """

    cur4.execute(my_request4)
    res4 = cur4.fetchall()

    # une section avec la liste des parties d'organismes reliés (via les transcrits) à ce gène (avec un lien vers la page
    # /parts/<part>/genes correspondante)
    my_request5 = f"""SELECT DISTINCT e.Atlas_Organism_Part
    FROM Expression as e
    NATURAL JOIN Trasncripts as t
    WHERE t.ensembl_gene_id = "{id}"
    AND atlas_organism_part IS NOT NULL
    """

    cur4.execute(my_request5)

    res5 = cur4.fetchall()

    return render_template('gene_id.html', object = res, obj = res4, obj5 = res5)


# Pour aller plus loin

@app.route("/genes/<id>/edit")
def afficher_formulaire(id):
    con4 = sqlite3.connect("ensembl_hs63_simple.sqlite")
    cur4 = con4.cursor()
    my_request6 = f"""SELECT chromosome_name, band, strand, gene_start, gene_end, associated_gene_name
    FROM Genes
    WHERE ensembl_gene_id = "{id}"
    """
    cur4.execute(my_request6)
    chromosome_name, band, strand, gene_start, gene_end, associated_gene_name = cur4.fetchone()

    return render_template('formulaire_pour_genes.html', chromosome_name = chrom4, band = band,
        strand = strand, gene_start = gene_start, gene_end = gene_end, associated_gene_name = associated_gene_name, id = id)
    
@app.route("/genes/<id>/edit/formulaire", methods=['POST']) # la méthode POST permet d'envoyer des données via la requête
    
def modif_info_gene(id): # obj: changer un élément dans la BDD et update la BDD
    data = request.form
    con4 = sqlite3.connect("ensembl_hs63_simple.sqlite")
    try:
        cur4 = con4.cursor()
        my_request7 = f"""UPDATE Genes
        SET chromosome_name='{data['Chromosome_Name']}', band='{data['Band']}', 
        strand = '{data["Strand"]}', gene_start = '{data['Gene_Start']}', gene_end = '{data['Associated_Gene_Name']}'
        WHERE ensembl_gene_id = "{id}"
        """
    cur4.execute(my_request7)
    con4.commit()
    finally:
        con4.close()
    return redirect(url_for("afficher_formulaire", id = id))

@app.route("/transcripts/<id>")
def fiche_indiv_transc(id):
    con4 = sqlite3.connect("ensembl_hs63_simple.sqlite")
    cur4 = con4.cursor()
    my_request4 = f"""SELECT t.Ensembl_Transcript_ID, t.Ensembl_Gene_ID, t.Transcript_Start, t.Transcript_End
    FROM Transcripts as t
    WHERE t.Ensembl_Transcript_ID = "{id}"
    """
    cur4.execute(my_request4)
    ensembl_transcript_id, ensembl_gene_id, transcript_start, transcript_end = cur4.fetchone()

    my_request5 = f"""SELECT DISTINCT e.Ensembl_Transcript_ID, e.Atlas_Organism_Part
    FROM Expression as e
    WHERE e.Ensembl_Transcript_ID = "{id}"
    """
    cur4.execute(my_request5)
    liste_expressions = cur4.fetchall()
    
    return render_template("fiche_indiv_transc.html", ensembl_transcript_id = ensembl_transcript_id,
    ensembl_gene_id = ensembl_gene_id, transcript_start = transcript_start, transcript_end = transcript_end, id = id, 
    liste_expressions = liste_expressions)


##################
### TP7
##################

from flask import jsonify # jsonify fabrique une requête qui contient du json

@app.route("/api/genes/<id>")
def api_gene_view(id):
    con = sqlite3.connect("ensembl_hs63_simple.sqlite")
    cur = con.cursor()
    # SQL REQUESTS
    my_request7 = f"""SELECT DISTINCT g.ensembl_gene_id, chromosome_name, band, strand, gene_start, gene_end,
    associated_gene_name, transcript_count
    FROM Genes as g
    NATURAL JOIN Transcripts as t
    WHERE ensembl_gene_id = "{id}"
    """
    cur.execute(my_request7)
    gene_row = cur.fetchone()

    gene_dict = unwrap_gene(gene_row)
    if not gene_dict:
        return jsonify({"error":"Ce gène n'existe pas"}), 404
    return str(gene_dict)

    # SQL REQUESTS FOR ASSOCIATED TRANSCRIPTS
    my_request8 = f"""SELECT DISTINCT t.ensembl_transcript_id, g.ensembl_gene_id, t.transcript_start,
    t.transcript_end, t.transcript_biotype
    FROM Transcripts as t
    NATURAL JOIN Genes as g
    WHERE ensembl_gene_id = "{id}"
    """
    cur.execute(my_request8)
    tr_row = cur.fetchall()

    tr_dict = unwrap_tr(tr_row)
    if not tr_dict:
        return jsonify({"error": "Il n'y a pas de transcrit associé à ce gène"}), 404
    return jsonify(gene_dict, tr_dict), 200

def unwrap_gene(row):
    if not row:
        return None
    return ({
        "ensembl_gene_id":row[0],
        "chromosome_name":row[1],
        "band":row[2],
        "strand":row[3],
        "gene_start":row[4],
        "gene_end":row[5],
        "associated_gene_name":row[6],
        "transcript_count":row[7]
    })

def unwrap_tr(tr_row):
    if not tr_row:
        return None
    return ({
        "ensembl_transcript_id":tr_row[0],
        "ensembl_gene_id":tr_row[1],
        "transcript_start":tr_row[2],
        "transcript_end":tr_row[3],
        "transcript_biotype":tr_row[4]
    })
