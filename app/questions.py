from flask_restful import reqparse, Resource

from app import db
from app.auth import jwt_required

QUESTION_PARSER = reqparse.RequestParser(bundle_errors=True)
QUESTION_PARSER.add_argument('question_subject', required=True,
                             help="Question subject is required")
QUESTION_PARSER.add_argument('question_body', required=True,
                             help="Question body is required")
QUESTION_PARSER.add_argument('Authorization', location='headers', required=True,
                             help="Token is required. Please login")

TOKEN_PARSER = reqparse.RequestParser(bundle_errors=True)
TOKEN_PARSER.add_argument('Authorization', location='headers',
                          required=True, help="Token is required. Please login")


class QuestionsApi(Resource):
    def get(self):
        """
            This endponint will get all the questions
            :return:
            """
        questions = db.qry("select  * from questions", fetch="all")
        for j in questions:
            j["date_posted"] = str(j["date_posted"])
        return questions, 200

    def post(self):
        args = QUESTION_PARSER.parse_args()

        user_id = jwt_required(args)
        try:
            user_id = int(user_id)
        except ValueError as e:
            return {"Error": "You have to be logged in"}, 403
        query = "INSERT into questions (question_subject, question_body, posted_by)" \
                " VALUES (%s, %s, %s)returning question_id, question_subject, " \
                "question_body, posted_by, date_posted"
        arguments = (
            args['question_subject'], args['question_body'], user_id)
        results = db.qry(query, arguments, fetch="one", commit=True)
        results["date_posted"] = str(results["date_posted"])
        return results, 201


def check_question_owner(question_id):
    query = "select users.account_id from questions inner join users on " \
            "(account_id=posted_by) where question_id = {}".format(question_id)
    question_result = db.qry(query, fetch="one")
    if question_result:
        return db.qry(query, fetch="one")["account_id"]


class QuestionGetUpdateDelete(Resource):
    def get(self, question_id):
        """
            This endpoint will fetch one question
            :rtype: jsonify
            """
        question = db.qry("select  * from questions where question_id = "
                          "'{}'".format(question_id), fetch="one")
        if not question:
            return {"Error": "No question found"}, 404
        question["date_posted"] = str(question["date_posted"])
        return question, 200

    def delete(self, question_id):
        """
            This function will delete a question
            :param question_id:
            :return:
            """
        args = TOKEN_PARSER.parse_args()
        user_id = jwt_required(args)
        try:
            user_id = int(user_id)
        except ValueError as e:
            return {"Error": "You have to be logged in"}
        if not user_id == check_question_owner(question_id):
            return {"Error": "UnAuthorised"}, 401
        query = "DELETE FROM questions WHERE question_id = {};".format(question_id)
        question = db.qry(query, commit=True)
        return question, 204

    def put(self, question_id):
        """
            This endpont will update subject and body when called
            :param question_id:
            :return:
            """
        args = QUESTION_PARSER.parse_args()

        user_id = jwt_required(args)
        try:
            user_id = int(user_id)
        except ValueError as e:
            return {"Error": "You have to be logged in"}
        if not user_id == check_question_owner(question_id):
            return {"Error": "UnAuthorised"}, 401
        params = args['question_subject'], args['question_body'], question_id
        query = "UPDATE questions SET question_subject = %s, " \
                "question_body = %s WHERE question_id = %s " \
                "RETURNING question_id, question_subject, " \
                "question_body, posted_by, date_posted;"
        question = db.qry(query, params, fetch="one")
        if not question:
            return {"Error": "No question found"}, 404
        question["date_posted"] = str(question["date_posted"])
        return question, 200
