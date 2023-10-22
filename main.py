from fastapi import FastAPI,Response,Request,status
# from typing import Annotated
# from fastapi.responses import 
from mysql_helper import mysql_helper
import uvicorn
import os
import jwt
import geopy.distance
from pydantic import BaseModel
import openai
import json
from typing import List
openai.api_key = '才不告訴你勒'

R = 6373.0


app = FastAPI()

SECRET_KEY = os.urandom(16)

@app.post('/login')
def login(
    user_name : str,
    password : str,
    response:Response
):
    with mysql_helper('JiaBar') as cur:
        try:
            sql_command = """
            SELECT * FROM User
            WHERE user_name = %s AND password = %s
            """
            cur.execute(sql_command,(user_name,password))

            data = cur.fetchall()
            if len(data) == 1:
                response.statuscode = status.HTTP_200_OK

                jwt_token = jwt.encode({'user_id':data[0]['id']},SECRET_KEY,algorithm='HS256')
                response.set_cookie('jwt_token',jwt_token)

                data[0]['success'] = True
                return data[0]
            else:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {
                    'message' : 'account or password error',
                    'success' : False
                }
        except:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                'message' : 'Login error',
                'success' : False
            }

@app.get('/restaurants')
def restaurants(longitude:float,latitude:float):
    with mysql_helper('JiaBar') as cur:
        sql_command = """
        SELECT * FROM Restaurant
        """
        cur.execute(sql_command)
        
        center_point = (latitude,longitude)
        target_distance = 3

        def distance_under(point):
            lon2 = float(point['longitude'])
            lat2 = float(point['latitude'])
            current_point = (lat2,lon2)
            distance = geopy.distance.geodesic(center_point, current_point).km
            return distance < target_distance

        filter_data  = []
        for i in cur.fetchall():
            if distance_under(i):
                filter_data.append(i)
        return filter_data

@app.get('/restaurant/{restaurant_id}')
def restaurant(restaurant_id:int):
    with mysql_helper('JiaBar') as cur:
        sql_command = """
        SELECT * FROM Restaurant WHERE id = %s
        """
        cur.execute(sql_command,(restaurant_id))
        data = cur.fetchone()

        sql_command = """
        SELECT AVG(rating)as restaurant_rating FROM Post WHERE restaurant_id = %s
        """ 
        cur.execute(sql_command,(restaurant_id))
        data['rating'] = cur.fetchone()['restaurant_rating']
        

        sql_command = """
        SELECT 
        Post.id as post_id,
        Post.content as post_content,
        Post.rating as post_rating,
        Post.image as post_image,
        Post.post_time,
        Restaurant.id as restaurant_id,
        Restaurant.name as restaurant_name,
        User.user_name,
        User.id as user_id,
        User.avatar_url as user_avatar
        FROM Post 
        INNER JOIN Restaurant 
        on Post.restaurant_id = Restaurant.id
        INNER JOIN User
        on Post.user_id = User.id
        WHERE Post.restaurant_id = %s
        """
        cur.execute(sql_command,(restaurant_id))
        data['posts'] = cur.fetchall()

        return data

@app.get('/posts')
def posts():
    with mysql_helper('JiaBar') as cur:
        sql_command = """
        SELECT 
        Post.id as post_id,
        Post.content as post_content,
        Post.rating as post_rating,
        Post.image as post_image,
        Post.post_time,
        Restaurant.id as restaurant_id,
        Restaurant.name as restaurant_name,
        User.user_name,
        User.id as user_id,
        User.avatar_url as user_avatar
        FROM Post 
        INNER JOIN Restaurant 
        on Post.restaurant_id = Restaurant.id
        INNER JOIN User
        on Post.user_id = User.id
        ORDER BY  Post.post_time DESC
        LIMIT 150
        """
        cur.execute(sql_command)
        return cur.fetchall()

@app.get('/post/{post_id}')
def post(post_id:int):
    with mysql_helper('JiaBar') as cur:
        sql_command = """
        SELECT 
        Post.id as post_id,
        Post.content as post_content,
        Post.rating as post_rating,
        Post.image as post_image,
        Restaurant.id as restaurant_id,
        Restaurant.name as restaurant_name,
        User.user_name,
        User.id as user_id,
        User.avatar_url as user_avatar
        FROM Post 
        INNER JOIN Restaurant 
        on Post.restaurant_id = Restaurant.id
        INNER JOIN User
        on Post.user_id = User.id
        WHERE Post.id = %s
        """
        cur.execute(sql_command,(post_id))
        
        return cur.fetchone()

@app.get('/comment/{post_id}')
def comment(post_id:int):
    with mysql_helper('JiaBar') as cur:
        sql_command = """
        SELECT 
        PostComment.id as comment_id,
        PostComment.content as comment_content,
        user_id,
        User.user_name
        FROM PostComment
        INNER JOIN User
        on PostComment.user_id = User.id
        WHERE PostComment.post_id =  %s
        """
        
        cur.execute(sql_command,(post_id))
        return {
            'post_id' : post_id,
            'comments' : cur.fetchall()
        }

@app.post('/new_post')
def new_post(
    request:Request
):
    with mysql_helper('JiaBar') as cur:

        sql_command = """
        
        """
        cur.execute(sql_command)


@app.post("/mind-test/guess")
def guess(answer1:int, answer2:int , answer3:int , longitude:float, latitude:float):
    def food_str(longitude:float,latitude:float):
        with mysql_helper('JiaBar') as cur:
            sql_command = """
            SELECT * FROM Restaurant
            """
            cur.execute(sql_command)
            
            center_point = (latitude,longitude)
            target_distance = 3

            def distance_under(point):
                lon2 = float(point['longitude'])
                lat2 = float(point['latitude'])
                current_point = (lat2,lon2)
                distance = geopy.distance.geodesic(center_point, current_point).km
                return distance < target_distance

            filter_data  = []
            for i in cur.fetchall():
                if distance_under(i):
                    filter_data.append(i)
            return str([i['name'] for i in filter_data])
    want = [
        ["輕鬆自在，想要休閒的感覺","肚子很餓，想要吃得飽足。","想要嘗鮮，尋找新的口感。","想喝杯飲料，稍微填填肚子。"],
        ["經典傳統，喜歡老店的味道。","創意新穎，願意嘗試新口感。","清淡健康，注重營養均衡。","甜食或飲料，解解渴或滿足甜蜜心情。"],
        ["需要高熱量的食物。","熱量無限制。","偏向少油少糖的食物。","想要小吃或點心。"]
    ]
    ask_str = ""
    ask_str += (f"我是一個不擅長抉擇的人，現在我要決定我要吃哪個店家，我想要的食物特徵有：「{want[0][answer1]},{want[1][answer2]},{want[2][answer3]}」，請幫我根據以下店家名稱，想出該店家有可能的菜單，並且自動幫我篩選出三個最適合我的店家：「")
    ask_str += food_str(longitude,latitude)
    ask_str += "」。備註：請直接幫我回答三個最匹配的店家名稱，不需要任何輔助文字，三個答案間請用「||」分開。"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant who understands foods,You only need to answer me the information I want, no need to make any remarks or supporting text or punctuation marks."},{"role": "user", "content": ask_str}],
        max_tokens=128,
        temperature=0.5,
    )

    restaurant_name = response["choices"][0]["message"]["content"].split('||')
    restaurant_data = []
    with mysql_helper('JiaBar') as cur:
        for i in restaurant_name:
            
            sql_command = """
            SELECT * FROM Restaurant WHERE name = %s
            """
            cur.execute(sql_command,(i))
            data = cur.fetchone()

            sql_command = """
            SELECT AVG(Post.rating)as restaurant_rating FROM Restaurant INNER JOIN Post WHERE Restaurant.name = %s
            """ 
            cur.execute(sql_command,(i))
            data['rating'] = cur.fetchone()['restaurant_rating']

            restaurant_data.append(data)
    return restaurant_data


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)