from flask import Flask, render_template, request, redirect, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SelectField, DecimalField
from wtforms.validators import DataRequired,InputRequired,NumberRange,Required
import numpy as np
import joblib

app=Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'any secret string'

class enterYourInfo(FlaskForm):
    validator_data_required=DataRequired(message="We need this information to estimate your obesity levels.")
    validator_input_required=InputRequired(message="We need this information to estimate your obesity levels.")
    message_error_range="Enter a value between {} and {}."

    #Fields:
    name=StringField("What is your name? ")

    sex=RadioField("What is your gender? ",validators=[validator_input_required],choices=[(1,"Male"),(0,"Female")],
                    coerce=int)

    age=IntegerField("What is your age? ",validators=[validator_data_required,NumberRange(min=0,max=122,
                    message=message_error_range.format(0,122))])

    height=DecimalField("What is your height in meters? ",validators=[validator_data_required,NumberRange(min=0.50,max=2.51,
                    message=message_error_range.format(0.5,2.51))])

    weight=DecimalField("What is your weight in kilograms? ",validators=[validator_data_required,NumberRange(min=3,max=597,
                    message=message_error_range.format(3,597))])

    family=RadioField("Has a family member suffered or suffers from overweight? ",
                    validators=[validator_input_required],
                    choices=[(1,"Yes"),(0,"No")],coerce=int)

    caloric_food=RadioField("Do you eat high caloric food frequently? ",
                    validators=[validator_input_required],
                    choices=[(1,"Yes"),(0,"No")],coerce=int)

    alcohol=RadioField("Do you drink alcohol? ",
                    validators=[validator_input_required],
                    choices=[(0,"I do not drink"),(1,"Yes")],coerce=int)

    vegetables=RadioField("Do you usually eat vegetables in your meals? ",
                    validators=[validator_input_required],
                    choices=[(0,"Never"),(1,"Sometimes"),(2,"Always")],coerce=int)

    meals=RadioField("How many main meals do you have daily? ",
                    validators=[validator_input_required],
                    choices=[(1,"One"),(2,"Two"),(3,"Three"),(4,"More than three")],coerce=int)

    snack=RadioField("Do you eat any food between meals? ",
                    validators=[validator_input_required],
                    choices=[(0,"No"),(1,"Sometimes"),(2,"Frequently"),(3,"Always")],coerce=int)

    water=RadioField("How much water do you drink daily? ",
                    validators=[validator_input_required],
                    choices=[(1,"Less than 1L"),(2,"Between 1 and 2L"),(3,"More than 3L")],coerce=int)

    sport=RadioField("How often do you have physical activity per week? ",
                    validators=[validator_input_required],
                    choices=[(0,"Less than two days"),(1,"Two days or more")],coerce=int)

    transport=RadioField("Which transportation do you usually use?",
                    validators=[validator_input_required],
                    choices=[(0,"Automobile or Motorbike"),(1,"Public Transportation"),(2,"Bike or Walking")],coerce=int)

@app.route('/')
def Welcome_Page():
    return render_template('mainPage.html')

@app.route('/Diagnostic',methods=["GET","POST"])
def Main_Page():
    form=enterYourInfo()
    if form.validate_on_submit():
        BMI=form.weight.data/(form.height.data**2)
        Bad_consumption_habits=form.alcohol.data+form.caloric_food.data
        MTRANS_FAF=form.transport.data+form.sport.data
        infos=[[form.sex.data,form.age.data,form.family.data,form.meals.data,
        form.snack.data,form.water.data,BMI,
        form.vegetables.data,Bad_consumption_habits,
        MTRANS_FAF]]
        model=joblib.load("model.save")
        prediction=model.predict(infos)
        session['predict'] = prediction[0]
        session['name'] = form.name.data.upper()
        return redirect('/Result')
    return render_template("diagnostic.html",form=form)

@app.route('/Result')
def pageResult():
    name = session.get('name', None)
    predict = session.get('predict', None)
    if(predict is None):
        return render_template("error.html")
    else:
        var2=" You should consult a doctor. "
        if predict == 'Insufficient_Weight':
            var = 'Underweighted'
        elif predict == 'Normal_Weight':
            var = 'of normal weight.'
            var2=" Congrats ! You have nothing to worry about. "
        elif predict == 'Overweight_Level_Iq':
            var = 'Overweighted (type 1)'
        elif predict == 'Overweight_Level_IIq':
            var = 'Overweighted (type 2)'
        elif predict == 'Obesity_Type_I':
            var = 'Obese (type 1)'
        elif predict == 'Obesity_Type_II':
            var = 'Obese (type 2)'
        elif predict == 'Obesity_Type_IIIq':
            var = 'Obese (type 3)'
        return render_template("predict.html", var = var,var2=var2,name = name)

@app.route('/AboutUs')
def pageAboutUs():
    return render_template("aboutus.html")

if __name__=='__main__':
    app.run(host="127.0.0.1",port=5001,debug=True)
