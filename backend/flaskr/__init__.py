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
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

    # abort 404 if no categories found
    if (len(categories_dict) == 0):
      abort(404)

    # return data to view
    return jsonify({
      'success': True,
      # 'categories': categories_dict
      "categories": {category.id: category.type for category in categories}
      # 'total_categories': len(Category.query.all())
    })


  #Create an endpoint to handle GET requests for questions, 
  @app.route("/questions")
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    # categories = Category.query.order_by(Category.type).all()
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type

    # abort 404 if no questions
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      "success": True,
      "questions": current_questions,
      #MENTOR SUGGESTED, DID NOT WORK -  "total_questions": len(selection)
      "total_questions": len(Question.query.all()),
      #DID NOT WORK -  'categories': categories_dict
      "categories": {category.id: category.type for category in categories},
      "current_category": None
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
    search = body.get('searchTerm', None)
    
    try:
      if search:
        selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
        )
        current_questions = paginate_questions(request, selection)

        return jsonify(
          {
            "success": True,
            "questions": current_questions,
            # "total_questions": len(selection.all())
            "total_questions": len(Question.query.all())
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
            "questions": current_questions,
            "total_questions": len(Question.query.all()),
          }
        )

    except:
      abort(422)



  #Create a GET endpoint to get questions based on category.
  @app.route('/categories/<int:id>/questions')
  def get_question_by_category(id):
    # Get category by id, try get questions from matching category
    category = Category.query.filter_by(id=id).one_or_none()

    try:
      selection = Question.query.filter_by(category=category.id).all()
      # paginate selected questions and return results
      current_questions = paginate_questions(request, selection)

      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(Question.query.all()),
        # "current_category": category_id
        "current_category": category.type
        # "categories": {category.id: category.type for category in categories}
      })

    except:
      abort(422)


    # Create a POST endpoint to get questions to play the quiz.
  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
        # This endpoint should take category and previous question parameters
    try:
      body = request.get_json()
      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)
      category_id = quiz_category['id']

      if category_id == 0:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(
          Question.id.notin_(previous_questions),
          Question.category == category_id).all()
      if(questions):
        question = random.choice(questions)

      return jsonify({
        'success': True,
        'question': question.format()
      })

    except Exception:
      abort(422)



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

    