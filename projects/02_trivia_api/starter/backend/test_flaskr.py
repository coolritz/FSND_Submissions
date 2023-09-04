import os
import unittest
import json
import collections
import collections.abc
from collections.abc import Mapping, MutableMapping

from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import db, setup_db, Question, Category
from dotenv import load_dotenv
from settings import TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASSWORD

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        #self.database_name = TEST_DB_NAME
        self.database_name = "trivia"
        #base_path = os.environ["DATABASE_PATH"]
        #self.database_path = 'postgresql://{}:{}@{}/{}'.format(TEST_DB_USER, TEST_DB_PASSWORD,'localhost:5432', self.database_name)
        #self.database_path='{}/{}'.format(base_path, self.database_name)
        self.database_path = 'postgresql://{}:{}@{}/{}'.format('postgres', '1408', 'localhost:5432', self.database_name)
        #setup_db(self.app, self.database_path)

        # binds the app to the current context
        #with self.app.app_context():
            #self.db = SQLAlchemy()
            #self.db.init_app(self.app)
            # create all tables
            #self.db.create_all()
    
        self.new_question={
            'question':'Name the Blue city of India',
            'answer':'Jodhpur',
            'category': 3,
            'difficulty':2
             }  
            
        self.quiz={
            'previous_questions':[1],
            'quiz_category':{
            'type':'Science',
            'id':'1'}
            } 

    def tearDown(self):
        """Executed after each test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))

    def test_get_questions_for_categories(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_questions_for_categories_not_found(self):
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], True)

    def test_questions_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_questions_valid_page(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 2)    

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/1100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], True)

    def test_paginate_questions(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_question(self): 
        new_search = {'searchTerm': 'Beetle'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_search_question_not_found(self): 
        new_search = {'searchTerm': 'xyz'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_add_question(self): 
        with self.app.app_context():
            total_available_question_before = len(Question.query.all())
            res = self.client().post('/questions', json=self.new_question)
            data = json.loads(res.data)
            total_available_question_after = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_available_question_after, total_available_question_before + 1)

    def test_quiz(self): 
        res = self.client().post('/quizzes', json=self.quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], True)
    
    def test_quiz_failure(self): 
        new_quiz = {'quiz_category': {'type': 'Entertainment'}}
        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], True) 


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()