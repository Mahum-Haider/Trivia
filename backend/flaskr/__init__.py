import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
  page = request.args.get("page", 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)


  #@TODO: Set up CORS. 
  CORS(app, resources={"/": {"origins": "*"}})

  #CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
      "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response
    


  #Create an endpoint to handle GET requests for all available categories.
  @app.route("/categories", methods=['GET'])
  def retrieve_categories():
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
      abort(404)

    return jsonify ({
      "success": True,
      "categories": {category.id : category.type for category in categories},
    })



  #Create an endpoint to handle GET requests for questions, 
  @app.route("/questions")
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.order_by(Category.type).all()

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      "success": True,
      "questions": current_questions,
      "total_questions": len(Question.query.all())
    })



  #Create an endpoint to DELETE question using a question ID. 
  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        "success": True,
        "deleted": question_id,
        "questions": current_questions,
        "total_questions": len(Question.query.all()),
      })

    except:
      abort(422)



  #Create an endpoint to POST a new question
  #Create a POST endpoint to get questions based on a search term. 
  @app.route("/questions", methods=["POST"])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get("answer", None)
    new_category = body.get("category", None)
    new_difficulty = body.get("difficulty", None)
    search = body.get('search', None)
    
    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(
                    Question.title.ilike("%{}%".format(search))
        )
        current_questions = paginate_questions(request, selection)

        return jsonify(
          {
            "success": True,
            "questions": current_questions,
            "total_questions": len(selection.all()),
          }
        )

      else:
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify(
          {
            "success": True,
            "created": question.id,
            "books": current_questions,
            "total_questions": len(Question.query.all()),
          }
        )

    except:
      abort(422)



  #Create a GET endpoint to get questions based on category.
  @app.route("/categories/<int:categories_id>/questions", methods=['GET'])
  def get_question_by_category(category_id):
    category = Category.query.get(id)
    if (category is None):
      abort(404)

    try:
      question = Question.query.filter(Question.category == str(category_id)).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(Question.query.all()),
        "current_category": category_id
      })

    except:
      abort(422)



  #Create a POST endpoint to get questions to play the quiz. 
  @app.route("/quizzes", methods=["POST"])
  def quiz_question():
    body = request.get_json()
    previousQuestions = body.get('previousQuestions', None)
    quizCategory = body.get('quizCategory', None)

    if quizCategory:
      if quizCategory['id'] == 0:
        quiz = Question.query.all()
      else:
        quiz = Question.query.filter_by(category=quizCategory['id']).all()
    if not quiz:
      abort(422)
    selected = []
    for question in quiz:
      if question.id not in previousQuestions:
        selected.append(question.format())
    if len(selected) != 0:
      result = random.choice(selected)
      return jsonify({
        'question': result
      })
    else:
      return jsonify({
        'question': False
      })



  # Create error handlers for all expected errors including 404 and 422. 
  @app.errorhandler(404)
  def not_found(error):
    return (
      jsonify({"success": False, "error": 404, "message": "resource not found"}),
      404,
    )
      

  @app.errorhandler(422)
  def unprocessable(error):
    return (
      jsonify({"success": False, "error": 422, "message": "unprocessable"}),
      422,
    )

        
  @app.errorhandler(400)
  def bad_request(error):
    return (
      jsonify({"success": False, "error": 400, "message": "bad request"}), 
      400,
    )

  @app.errorhandler(405)
  def not_allowed(error):
    return (
      jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
      405,
    )


  return app

    