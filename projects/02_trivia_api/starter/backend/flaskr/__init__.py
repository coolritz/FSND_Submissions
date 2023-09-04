import os
import random
import collections
import collections.abc

from collections.abc import Mapping, MutableMapping
from sqlalchemy import except_, true, func
from unicodedata import category
from models import db, setup_db, Question, Category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy, Pagination
from flask_cors import CORS,cross_origin

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the DONEs
  '''
  #CORS(app)
  CORS(app,resources={r"/" : {'origins': '*'}})
  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
   response.headers.add('Access-control-Allow-Headers', 'Content-Type, Authorization')
   response.headers.add('Access-control-Allow-Headers', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
   return response
  
  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories') 
  def get_categories():
      try:
          data = {}
          categories = Category.query.order_by(Category.type).all()
          
          for category in categories:
            data[category.id] = category.type
                
          return jsonify({
           'success':True,
           'categories': data
          })

      except Exception as e:
         print(e)
         abort(404)  

  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  def paginate_questions(request, selection):
      questions = []
      page = request.args.get('page', 1, type=int)
      start = (page-1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      questions = [question.format() for question in selection]
      current_questions = questions[start:end]
      return current_questions
  

  @app.route('/questions') 
  def get_questions():
      try:
          #selection = Question.query.all()
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)
          data={}
          categories_list = Category.query.order_by(Category.type).all()

          for category in categories_list:
             data[category.id]=category.type
                       
          return jsonify({
             'success':True,
             'questions': current_questions,
             'total_questions': len(selection),
             'categories': data 
            })

      except Exception as e:
         print(e)
         abort(404)

  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE']) 
  def delete_questions(question_id):
     
    try:
        #question=Question.query.order_by(Question.id).all()
        question=Question.query.filter_by(id=question_id).one_or_none()
        question.delete()
        return jsonify({
           'success':True,
           'deleted': question_id,
        })  
    except Exception as e:
      print(e)
      abort(422)

  '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  @cross_origin()
  def create_questions():
      body = request.get_json()
      searchVal=body.get('searchTerm',None)
      selection=[]
      
      if searchVal:
         try:
            questions=Question.query.filter(Question.question.ilike('%'+ searchVal + '%')).all()
            current_questions=paginate_questions(request,selection)

            if len(current_questions) == 0:
               abort(422)
            else:
               return jsonify({ 
                      'success':True,
                      'questions': current_questions,
                      'total_questions': len(current_questions)
                  })  
         except Exception as e:
             print(e)
             abort(422)
      else:
            try:
               new_question = body.get('question', None)
               new_answer = body.get('answer', None)
               new_category = body.get('category', None)
               new_difficulty = body.get('difficulty', None)
               question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
               question.insert()
              
               selection = Question.query.all()
               current_questions = paginate_questions(request, selection)

               return jsonify({ 
                    "success": True, 
                    "created": question.id, 
                    "questions": current_questions, 
                    "total_questions": len(current_questions)
               })
            except:   
               abort(422)   
      
  '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm')
    if search_term:
        try:
           search_results = Question.query.filter(
              Question.question.ilike(f'%{search_term}%')).all()   
           current_questions = paginate_questions(request, search_results)
           return jsonify({
              'success': True,
              'questions': current_questions,
              'total_questions': len(search_results),
           })
        except Exception as e:
           abort(404) 

  '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
      try:
        selection=Question.query.filter(Question.category == str(category_id)).all()

        if len(selection) > 0:
           current_questions = paginate_questions(request, selection)
     
           return jsonify({
              'success':True,
              'questions':current_questions,
              'total_questions':len(selection),
              'currentCategory':''
            })
        else:
           abort(404)
      except Exception as e:
        print(e)
        abort(404)
  '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
      try:
          body = request.get_json()
          #selection = []
          #if not ('quiz_category' in body and 'previous_question' in body and body.get('quiz_category') != '' and body.get('previous_questions') != ''):
          #  abort(422)
          
          category = body.get('quiz_category', None)
          previous_questions = body.get('previous_questions', None)

          if category['type'] == 'click':
             available_questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
          else:
             available_questions = Question.query.filter_by(
                category=category['id']).filter(~Question.id.in_(previous_questions)).all() 
             new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

          return jsonify({
              'success': True,
              'question':new_question
          })    
      except Exception as e:
        print(e)
        abort(404)
  '''
  
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
          "success": True, 
          "error": 404,
          "message": "Not found says ritesh "
        }), 404

  @app.errorhandler(422)
  def not_processable(error):
    return jsonify({
        "success": True, 
        "error": 422,
        "message": "Unprocessable says ritesh"
        }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": True, 
        "error": 400,
        "message": "Bad Request says ritesh"
        }), 400   

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
        "success": True, 
        "error": 405,
        "message": "Method Not Allowed says ritesh"
        }), 405    
          
  return app

    