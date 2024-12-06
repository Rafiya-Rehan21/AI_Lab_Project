import streamlit as st
import pandas as pd
from Generate_Recommendations import Generator
from random import uniform as rnd
from ImageFinder.ImageFinder import get_images_links as find_image
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Automatic Diet Recommendation", page_icon="💪",layout="wide")

nutritions_values = ['Calories', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']

# Streamlit states initialization
if 'person' not in st.session_state:
    st.session_state.generated = False
    st.session_state.recommendations = None
    st.session_state.person = None
    st.session_state.weight_loss_option = None

class Person:
    def __init__(self, age, height, weight, gender, activity, meals_calories_perc, weight_loss):
        self.age = age
        self.height = height
        self.weight = weight
        self.gender = gender
        self.activity = activity
        self.meals_calories_perc = meals_calories_perc
        self.weight_loss = weight_loss

    def calculate_bmi(self):
        bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        return bmi

    def display_result(self):
        bmi = self.calculate_bmi()
        bmi_string = f'{bmi} kg/m²'
        if bmi < 18.5:
            category = 'Underweight'
            color = 'Red'
        elif 18.5 <= bmi < 25:
            category = 'Normal'
            color = 'Green'
        elif 25 <= bmi < 30:
            category = 'Overweight'
            color = 'Yellow'
        else:
            category = 'Obesity'
            color = 'Red'
        return bmi_string, category, color

    def calculate_bmr(self):
        if self.gender == 'Male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return bmr

    def calories_calculator(self):
        activities = ['Little/no exercise', 'Light exercise', 'Moderate exercise (3-5 days/wk)', 'Very active (6-7 days/wk)', 'Extra active (very active & physical job)']
        weights = [1.2, 1.375, 1.55, 1.725, 1.9]
        weight = weights[activities.index(self.activity)]
        maintain_calories = self.calculate_bmr() * weight
        return maintain_calories

    def generate_recommendations(self):
        total_calories = self.weight_loss * self.calories_calculator()
        recommendations = []
        for meal in self.meals_calories_perc:
            meal_calories = self.meals_calories_perc[meal] * total_calories
            if meal == 'breakfast':
                recommended_nutrition = [meal_calories, rnd(10, 30), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75), rnd(4, 10), rnd(0, 10), rnd(30, 100)]
            elif meal == 'launch':
                recommended_nutrition = [meal_calories, rnd(20, 40), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75), rnd(4, 20), rnd(0, 10), rnd(50, 175)]
            elif meal == 'dinner':
                recommended_nutrition = [meal_calories, rnd(20, 40), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75), rnd(4, 20), rnd(0, 10), rnd(50, 175)]
            else:
                recommended_nutrition = [meal_calories, rnd(10, 30), rnd(0, 4), rnd(0, 30), rnd(0, 400), rnd(40, 75), rnd(4, 10), rnd(0, 10), rnd(30, 100)]
            generator = Generator(recommended_nutrition)
            recommended_recipes = generator.generate().json()['output']
            recommendations.append(recommended_recipes)
        for recommendation in recommendations:
            for recipe in recommendation:
                recipe['image_link'] = find_image(recipe['Name'])
        return recommendations

class Display:
    def __init__(self):
        self.plans = ["Maintain weight", "Mild weight loss", "Weight loss", "Extreme weight loss"]
        self.weights = [1, 0.9, 0.8, 0.6]
        self.losses = ['-0 kg/week', '-0.25 kg/week', '-0.5 kg/week', '-1 kg/week']

    def display_bmi(self, person):
        st.header('🧑‍⚕️ BMI CALCULATOR')
        bmi_string, category, color = person.display_result()
        st.metric(label="Body Mass Index (BMI)", value=bmi_string)
        new_title = f'<p style="font-family:sans-serif; color:{color}; font-size: 25px;">{category}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        st.markdown(
            """
            Healthy BMI range: 18.5 kg/m² - 25 kg/m².
            """)

    def display_calories(self, person):
        st.header('🔥 CALORIES CALCULATOR')
        maintain_calories = person.calories_calculator()
        st.write('The results show a number of daily calorie estimates that can be used as a guideline for how many calories to consume each day to maintain, lose, or gain weight at a chosen rate.')
        for plan, weight, loss, col in zip(self.plans, self.weights, self.losses, st.columns(4)):
            with col:
                st.metric(label=plan, value=f'{round(maintain_calories * weight)} Calories/day', delta=loss, delta_color="inverse")

    def display_recommendation(self, person, recommendations):
        st.header('🍽️ DIET RECOMMENDATOR')
        with st.spinner('Generating recommendations...'):
            meals = person.meals_calories_perc
            st.subheader('Recommended recipes:')
            for meal_name, column, recommendation in zip(meals, st.columns(len(meals)), recommendations):
                with column:
                    st.markdown(f'##### {meal_name.upper()}')
                    for recipe in recommendation:
                        recipe_name = recipe['Name']
                        expander = st.expander(recipe_name)
                        recipe_link = recipe['image_link']
                        recipe_img = f'<div><center><img src={recipe_link} alt={recipe_name}></center></div>'
                        nutritions_df = pd.DataFrame({value: [recipe[value]] for value in nutritions_values})

                        expander.markdown(recipe_img, unsafe_allow_html=True)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Nutritional Values (g):</h5>', unsafe_allow_html=True)
                        expander.dataframe(nutritions_df)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Ingredients:</h5>', unsafe_allow_html=True)
                        for ingredient in recipe['RecipeIngredientParts']:
                            expander.markdown(f"""
                                        - {ingredient}
                            """)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Recipe Instructions:</h5>', unsafe_allow_html=True)
                        for instruction in recipe['RecipeInstructions']:
                            expander.markdown(f"""
                                        - {instruction}
                            """)
                        expander.markdown(f'<h5 style="text-align: center;font-family:sans-serif;">Cooking and Preparation Time:</h5>', unsafe_allow_html=True)
                        expander.markdown(f"""
                                - Cook Time       : {recipe['CookTime']}min
                                - Preparation Time: {recipe['PrepTime']}min
                                - Total Time      : {recipe['TotalTime']}min
                            """)

    def display_meal_choices(self, person, recommendations):
        st.subheader('Choose your meal composition:')
        if len(recommendations) == 3:
            breakfast_column, launch_column, dinner_column = st.columns(3)
            with breakfast_column:
                breakfast_choice = st.selectbox(f'Choose your breakfast:', [recipe['Name'] for recipe in recommendations[0]])
            with launch_column:
                launch_choice = st.selectbox(f'Choose your launch:', [recipe['Name'] for recipe in recommendations[1]])
            with dinner_column:
                dinner_choice = st.selectbox(f'Choose your dinner:', [recipe['Name'] for recipe in recommendations[2]])

            person.meals_calories_perc = {'breakfast': breakfast_choice, 'launch': launch_choice, 'dinner': dinner_choice}
