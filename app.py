from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
import csv
import pandas as pd
import numpy as np
import json
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

data2 = pd.read_csv("static/data/KickStarter2018.csv")
stopwords = ["video,dance,journalism,crafts,theater,photography,comics,design,fashion,games,food,publishing,art,technology,film,music,category,kickstart,kickstarter,pledge,goal,now,should,don't,just,will,can,very,too,than,so,same,own,only,not,nor,no,such,some,other,most,more,few,each,both,any,all,how,why,where,when,there,here,once,then,further,again,under,over,off,on,out,in,down,up,from,to,below,above,after,before,during,through,into,between,against,about,with,for,by,at,of,while,until,as,because,or,if,but,and,the,an,a,doing,did,does,do,having,had,has,have,being,been,be,were,was,are,is,am,those,these,that,this,whom,who,which,what,themselves,theirs,their,them,they,itself,its,it,herself,hers,her,she,himself,his,him,he,yourselves,yourself,yours,your,you,ourselves,ours,our,we,myself,my,me,i"]

@app.route('/', methods=['GET', 'POST'])
def index():
    temp = data2[data2.state == 'successful'].blurb
    text = " ".join(temp.iloc[i] for i in range(len(temp)))

    return render_template('main.html', successful_text=[text, stopwords])

@app.route('/maps')
def maps():
    return render_template('maps.html')

@app.route('/insights', methods = ['POST', 'GET'])
def insights():
    if request.method == 'POST':
        result = request.form
        return render_template('insights.html', data1=result['goal'])
    return render_template('insights.html', data1=0)

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/spotlight')
def spotlight():
    return render_template('spotlight.html')

@app.route('/world_data')
def world_data():
    with open('static/data/countries.csv', mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        my_dict = {}
        for row in reader:
            if row[1] not in my_dict:
                my_dict[row[1]] = [row[0], row[2]]
    
    countries = data2.loc_country.value_counts()
    country_data = []
    for index, item in zip(countries.index, countries.values):
        each_data = {}
        if index in my_dict:
            each_data['id'] = str(my_dict[index][1])
            each_data['country'] = str(my_dict[index][0])
        each_data['projects'] = str(item)
        
        country_data.append(each_data)

    return jsonify(country_data)

@app.route('/usa_data')
def usa_data():
    with open('static/data/us_state.csv', mode='r') as infile:
        reader = csv.reader(infile)
        next(reader)
        my_dict = {}
        for row in reader:
            if row[1] not in my_dict:
                my_dict[row[1]] = row[0]
                
    usa_data = data2[data2.loc_country == "US"]
    states = usa_data.loc_state.value_counts()
    usa = []
    unattended = []
    for index, item in zip(states.index, states.values):
        each_data = {}
        if index in my_dict:
            each_data['code'] = index
            each_data['state'] = my_dict[index]
            each_data['projects'] = int(item)
            usa.append(each_data)
        elif index:
            temp = index.split("-")[-1]
            each_data['code'] = temp.upper()
            each_data['state'] = my_dict[temp.upper()]
            each_data['projects'] = int(item)
            unattended.append(each_data)
        
    for val1 in unattended:
        for val2 in usa:
            if val1['state'] in val2['state']:
                val2['projects'] += val1['projects']
                
    for val in usa:
        temp = usa_data[usa_data['loc_state'] == val['code']]
        positive = temp[temp['state'] == 'successful'].state.value_counts()
        negative = temp[temp['state'] == 'failed'].state.value_counts()
        category = temp.cat_parent.value_counts()
        val['successful'] = int(positive.values)
        val['fail'] = int(negative.values)
        val['category'] = category.index[0]

    return jsonify(usa)

# @app.route('/usa_json')
# def usa_json():
#     with open('static/data/USA.json') as json_file:  
#         data = json.load(json_file)
        
#     return jsonify(data)

@app.route('/get_piechart_data')
def get_piechart_data():
    category_perc = round(data2["cat_parent"].value_counts()/len(data2["cat_parent"])*100,2)
    pieChartData = []
    for index, item in zip(category_perc.index, category_perc.values):
        each_data = {}
        each_data['category'] = index
        each_data['measure'] = round(item, 1)

        pieChartData.append(each_data)

    return jsonify(pieChartData)

@app.route('/get_barchart_data')
def get_barchart_data():
    barChartData = []
    percentage_success = round(data2["state"].value_counts()/len(data2["state"])*100,2)
    for index, item in zip(percentage_success.index, percentage_success.values):
        each_data = {}
        each_data['group'] = "All"
        each_data['category'] = index
        each_data['measure'] = round(item, 1)

        barChartData.append(each_data)

    for value in data2.cat_parent.unique():
        filtered = data2[data2.cat_parent == value]
        percentage_data = round(filtered["state"].value_counts()/len(filtered["state"])*100, 2)
        for index, item in zip(percentage_data.index, percentage_data.values):
            each_data = {}
            each_data['group'] = str(value)
            each_data['category'] = index
            each_data['measure'] = round(item, 2)

            barChartData.append(each_data)

    return jsonify(barChartData)

@app.route('/line_chart_data')
def line_chart_data():
    line_chart_data = [
        {"year" : "2005", "value": 771900},
        {"year" : "2006", "value": 771500},
        {"year" : "2007", "value": 770500},
        {"year" : "2008", "value": 770400},
        {"year" : "2009", "value": 771000},
        {"year" : "2010", "value": 772400},
        {"year" : "2011", "value": 774100},
        {"year" : "2012", "value": 776700},
        {"year" : "2013", "value": 777100},
        {"year" : "2014", "value": 779200},
        {"year" : "2015", "value": 782300}
    ]
    # by_year = data2.year.value_counts()
    # by_month = data2.month.value_counts()
    # line_chart_data = []
    # num_month = {"1": "Jan", "2": "Feb", "3": "Mar", "4": "Apr", "5": "May", "6": "Jun", "7": "Jul", "8": "Aug", "9": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}

    # for index, item in zip(by_year.index, by_year.values):
    #     each_data = {}
    #     each_data['key'] = str(index)
    #     each_data['value'] = int(round(item, 2))
    #     each_data['type'] = 'year'
        
    #     line_chart_data.append(each_data)
        
    # for index, item in zip(by_month.index, by_month.values):
    #     each_data = {}
    #     if str(index) in num_month:
    #         each_data['key'] = num_month[str(index)]
    #     each_data['value'] = int(round(item, 2))
    #     each_data['type'] = 'month'
        
    #     line_chart_data.append(each_data)
    
    return jsonify(line_chart_data)

@app.route('/spotlight_data')
def get_spotlight_data():
    spotlight = data2[data2.spotlight == True]
    spotlight['hasName'] = spotlight['name'].apply(lambda x: str(x).isalpha())
    spotlight = spotlight[spotlight.hasName == True]
    spotlight['converted_pledged_amount'] = spotlight['converted_pledged_amount'].astype('float32')
    spotlight['goal'] = spotlight['goal'].astype('float32')
    spotlight['pledge_percentage'] = spotlight['converted_pledged_amount'].divide(spotlight['goal'], fill_value=0)*100
    spotlight = spotlight[spotlight.pledge_percentage <= 1000]
    categories = spotlight.cat_parent.unique()
    spotlight_data = []
    for cat in categories:
        cat_data = spotlight[spotlight.cat_parent == cat]
        cat_data = cat_data.sort_values(by=['pledge_percentage'], ascending=False)
        cat_data = cat_data.head(5)
        
        for i in range(len(cat_data)):
            each_data = {}
            each_data['projID'] = int(cat_data.iloc[i].project_id)
            each_data['name'] = str(cat_data.iloc[i]["name"])
            try:
                each_data['projURL'] = cat_data.iloc[i].project_url.split(" ")[0]
            except:
                each_data['projURL'] = cat_data.iloc[i].project_url
            each_data['cat_parent'] = str(cat)
            each_data['category'] = str(cat_data.iloc[i].cat_name)
            each_data['blurb'] = str(cat_data.iloc[i].blurb)
            each_data['priority'] = int(cat_data.iloc[i].pledge_percentage)
            
            spotlight_data.append(each_data)

    return jsonify(spotlight_data)

@app.route("/continent_category_data")
def continent_category_data():
    continent_list = data2["continent"].unique()
    continent_data = []
    
    for continent in continent_list:
        temp_data = data2[data2.continent == continent]
        category_perc = temp_data["cat_parent"].value_counts()
        
        for index, item in zip(category_perc.index, category_perc.values):
            each_data = {}
            each_data['continent'] = str(continent)
            each_data['area'] = str(index)
            each_data['value'] = int(item)

            continent_data.append(each_data)
            
    return jsonify(continent_data)

if __name__ == '__main__':
   app.run(debug = True)