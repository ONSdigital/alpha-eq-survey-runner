class Questionnaire:

    def __init__(self):
        self.survey_id = None
        self.title = None
        self.overview = None
        self.questionnaire_id = None
        self.questionnaire_title = None
        self.questions = []

    def add_question(self, question):
        self.questions.append(question)
