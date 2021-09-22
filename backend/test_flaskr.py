import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from settings import DB_NAME, DB_USER, DB_PASSWORD
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Who invented Peanut Butter?", "answer": "George Washington Carver", "category": 4, "difficulty": 3}
        self.input_data = {"previous_questions": 2, "quiz_category":  {"id": 5, "type": "Entertainment"}}


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    #Paginated questions 
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    #Paginated questions failure
    def test_get_paginated_questions_failure(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")



    #Retrieve Categories
    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data["categories"]))

    #Retrieve Categories for failure 
    def test_retrieve_categories_failure(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')



    #Retrieve Questions
    def test_retrieve_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    #Retrieve Questions for failure
    def test_retrieve_questions_failure(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'Not found')



    #Delete Questions
    def test_delete_question(self):
        res = self.client().delete("/questions/11")
        data  = json.loads(res.data)

        question = Question.query.filter(Question.id == 11).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 11)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    #Delete Questions for failure
    def test_delete_question_failure(self):
        res = self.client().delete("/questions/11")
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'Unprocessable entity')



    # Add Questions
    def test_create_question(self):
        test_question = {'question': 'test question', 'answer': 'test answer', 'category': '1', 'difficulty': '1'}
        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    # Add Questions for failure
    def test_create_question_failure(self):
        test_question = {'question': 'test question', 'answer': 'test answer', 'category': '1', 'difficulty': '1'}
        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'Not found')



    # Search Questions
    def test_search_questions(self):
        test_search = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', json=test_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # Search Questions failure.
    def test_search_questions_failure(self):
        test_search = {'searchTerm': 'a'}
        res = self.client().post('/questions/', json=test_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found.')



    #Retrieve Questions based on Categories
    def test_create_new_question(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    #Retrieve Questions based on Categories failure
    def test_create_new_question_failure(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'Not found')
        


    #Play Quiz
    def tes_quiz_question(self):
        res = self.client().post("/quizzes", json=self.input_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    #Play Quiz failure
    def tes_quiz_question_failure(self):
        res = self.client().post("/quizzes", json=self.input_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found.')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()