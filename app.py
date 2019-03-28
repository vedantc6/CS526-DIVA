from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
import csv
import pandas as pd
import numpy as np
import json
from config import Config
from sklearn.externals import joblib
import pickle

app = Flask(__name__)
app.config.from_object(Config)

data2 = pd.read_csv("static/data/KickStarter2018.csv")
stopwords = ["video,dance,journalism,crafts,theater,photography,comics,design,fashion,games,food,publishing,art,technology,film,music,category,kickstart,kickstarter,pledge,goal,now,should,don't,just,will,can,very,too,than,so,same,own,only,not,nor,no,such,some,other,most,more,few,each,both,any,all,how,why,where,when,there,here,once,then,further,again,under,over,off,on,out,in,down,up,from,to,below,above,after,before,during,through,into,between,against,about,with,for,by,at,of,while,until,as,because,or,if,but,and,the,an,a,doing,did,does,do,having,had,has,have,being,been,be,were,was,are,is,am,those,these,that,this,whom,who,which,what,themselves,theirs,their,them,they,itself,its,it,herself,hers,her,she,himself,his,him,he,yourselves,yourself,yours,your,you,ourselves,ours,our,we,myself,my,me,i"]

def predict_function(result):
    data = pd.read_csv('static/data/basic_features.csv')
    l = result['desc'].split(" ")
    s = ""
    parent_category = result['parent_category']
    for val in l:
        if val not in stopwords:
            s += val
    if parent_category == "filmvideo":
        parent_category = "film & video"
    user_df = pd.DataFrame([[float(result['goal']), True, result['country'], result['category'], parent_category, 'failed', result['campaign_length'], len(s)]], columns=data.columns)
    print(user_df)
    data = data.append(user_df, ignore_index=True)
    data =  pd.get_dummies(data, columns=['loc_country','cat_name', 'cat_parent'])
    data.drop(columns=['state'], inplace=True)
    user_data = data.iloc[-1,:]
    user_data = np.array(user_data.values, dtype=np.float64).reshape(1,-1)
    loaded_model = joblib.load('static/data/lr_no_nlp.pkl')
    probs = loaded_model.predict_proba(user_data)
    return int(probs[0][1]*100)

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
        print(result)
        value = predict_function(result)
        return render_template('insights.html', data1=value)
    return render_template('insights.html', data1=0)

@app.route('/statistics', methods = ['POST', 'GET'])
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
    new_data = pd.read_csv("static/data/line_chart_ma.csv")
    new_data['MA'] = new_data['value'].rolling(window=5).mean()
    new_data = new_data.dropna(axis=0)
    
    data = []

    for i in range(len(new_data)):
        val = new_data["MA"].iloc[i]
        date = new_data["date"].iloc[i]
        each_data = {}
        each_data["date"] = date
        each_data["value"] = int(val)

        data.append(each_data)

    return jsonify(data)
    # line_chart_data = [
    #     {"year" : "2005", "value": 771900},
    #     {"year" : "2006", "value": 771500},
    #     {"year" : "2007", "value": 770500},
    #     {"year" : "2008", "value": 770400},
    #     {"year" : "2009", "value": 771000},
    #     {"year" : "2010", "value": 772400},
    #     {"year" : "2011", "value": 774100},
    #     {"year" : "2012", "value": 776700},
    #     {"year" : "2013", "value": 777100},
    #     {"year" : "2014", "value": 779200},
    #     {"year" : "2015", "value": 782300}
    # ]

    # return jsonify(line_chart_data)

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

@app.route('/category_treemap')
def get_category_treemap():
    category_map_data = []
    colors = ["#e377c2", "#d62728", "#2ca02c", "#ff7f0e", "#c5b0d5", "#ff9896", "#1f77b4", "#f7b6d2", "#aec7e8", "#9467bd", "#ffbb78", "#98df8a", "#8c564b", "#c49c94", "#7f7f7f"]
    i = 0
    for value in data2.cat_parent.unique():
        each_data = {}
        if value not in each_data:
            each_data["name"] = value
            each_data["children"] = []
            each_data["color"] = colors[i]
            
        filtered = data2[data2.cat_parent == value]
        category = filtered.cat_name.unique()
        for cat in category:
            child_dict = {}
            filtered_cat = filtered[filtered.cat_name == cat]
            filtered_cat["converted_pledged_amount"] = filtered_cat["converted_pledged_amount"].apply(int)
            percentage_success = filtered_cat["converted_pledged_amount"].sum()
            if "name" not in child_dict:
                child_dict["name"] = cat
                child_dict["value"]= int(percentage_success)
                
            each_data["children"].append(child_dict)
                
        category_map_data.append(each_data)
        i += 1
            
    return jsonify(category_map_data)

if __name__ == '__main__':
   app.run(debug = True)