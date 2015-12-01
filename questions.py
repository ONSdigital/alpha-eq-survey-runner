import importlib
from branching import JumpTo
from validators import ValidationResult


class Question(object):
    def __init__(self, question_schema, parent=None):
        self.parent = parent
        self.skipping = False
        self._schema = question_schema
        self.type = question_schema['questionType']
        self.question_text = question_schema['questionText']
        self.question_help = question_schema['questionHelp']
        self._reference = question_schema['questionReference']
        self._repeating = self._build_repeating(question_schema['repeating'])
        self.display_properties = None
        self.validation = self._build_validation(question_schema['validation'])
        self.parts = self._build_parts(question_schema['parts'])
        self.children = None
        self.display_conditions = None
        self.skip_conditions = []
        self.branch_conditions = self._build_branch_conditions(question_schema['branchConditions'])
        self.allWarningsAccepted = True
        self.answers = []
        self.accepted = []
        self.justifications = []
        self.validation_results = []
        self.set_repetition(0)

    def set_user_data(self, user_data):
        if 'answer' in user_data:
            self.answers = user_data['answer']
        if 'accepted' in user_data:
            self.accepted = user_data['accepted']
        if 'justifications' in user_data:
            self.justifications = user_data['justifications']

        if self.repeats():
            self.set_repetition(len(self.answers))

    def get_user_data(self):
        return {
            'answer': self.answers,
            'accepted': self.accepted,
            'justifications': self.justifications
        }

    @staticmethod
    def factory(schema, parent=None):
        if schema['questionType'] == 'InputText': return InputTextQuestion(schema, parent)
        if schema['questionType'] == 'TextBlock': return TextBlock(schema, parent)
        if schema['questionType'] == 'MultipleChoice': return MultipleChoiceQuestion(schema, parent)
        if schema['questionType'] == 'QuestionGroup': return QuestionGroup(schema, parent)
        if schema['questionType'] == 'CheckBox': return CheckBoxQuestion(schema, parent)
        if schema['questionType'] == 'Dropdown': return DropdownQuestion(schema, parent)

    def _build_validation(self, validation_schema):
        rules = []

        for validation in validation_schema:
            # find the validaton class and instantiate it
            RuleClass = getattr(importlib.import_module('validators'), validation['condition'].capitalize())
            # this loads the class from the validators.py file
            rule = RuleClass(validation)
            rules.append(rule)

        return rules

    def _build_repeating(self, schema):
        if schema:
            if 'count' in schema:
                # we are repeating a specific number of times
                if 'response' in schema['count']:
                    # we are repeating based on a previous response
                    return True

                if 'value' in schema['count']:
                    # not implemented, just here as a placeholder for the thought
                    return True


            if 'until' in schema:
                # not implemented, just here as a placeholder for the thought
                return False

        return False

    def _build_parts(self, schema):
        parts = []
        for part in schema:
            parts.append(part['value'])

        return parts

    def _build_branch_conditions(self, branch_conditions_schema):
        branch_conditions = []
        for condition in branch_conditions_schema:
             if condition['jumpTo'] and condition['jumpTo']['condition']['value']['is']:
                jumpTo = JumpTo(condition['jumpTo']['question'], self.get_reference(), condition['jumpTo']['condition']['value']['is'])
                branch_conditions.append(jumpTo)

        return branch_conditions

    def branches(self):
        for rule in self.branch_conditions:
            if rule.trigger == self.get_reference() and rule.state == self.answers[self.repetition]:
                # need to append the EQ_ rule.target comes from the schema
                return "EQ_" + rule.target

        return None

    def get_branch_target(self):
        return self.branches()

    def validate(self):
        self.validation_results = []
        for repetition in range(0, self.repetition + 1):
            if len(self.answers) > repetition:
                self.validation_results.append(self._validate_answer(self.answers[repetition]))

        return self.validation_results

    def _validate_answer(self, answer):
        errors = []
        warnings = []

        for rule in self.validation:
            if rule.get_type() == 'error':
                if not rule.is_valid(answer):
                    errors.append(rule.get_message(answer))
                    break
            elif rule.get_type() == 'warning':
                if not rule.is_valid(answer):
                    # All warnings need to be recorded to populate checkboxes and messages
                    warnings.append(rule.get_message(answer))

        result = ValidationResult(errors, warnings, self.accepted[self.repetition])

        return result



    def get_warnings(self, reference=None):
        return self.warnings[self.repetition]

    def get_errors(self, reference=None):
        return self.errors[self.repetition]

    def get_accepted(self):
        return self.accepted[self.repetition]

    def get_branch_conditions(self):
        return self.branch_conditions

    def has_branch_conditions(self):
        return len(self.branch_conditions) > 0

    def get_skip_conditions(self):
        return self.skip_conditions

    def has_skip_conditions(self):
        return len(self.skip_conditions) > 0

    def get_question_by_reference(self, reference):
        return None

    def get_reference(self):
        if self.parent:
            return self.parent.get_reference() + '_' + self._reference
        else:
            return "EQ_" + self._reference

    def repeats(self):
        return self._repeating

    def get_repetition(self):
        return self.repetition

    def set_repetition(self, repetition):
        while len(self.answers) <= repetition:
            self.answers.append('')
            self.justifications.append(False)
            self.accepted.append(False)

        self.repetition = repetition

    def get_answer(self):
        if self.repetition >= len(self.answers):
            return None

        return self.answers[self.repetition]

    def update(self, answer):
        self.answers[self.repetition] = answer

    def set_warning(self, warning):
        self.warnings[self.repetition] = warning

    def set_accepted(self, accepted):
        self.accepted[self.repetition] = accepted

class MultipleChoiceQuestion(Question):
    def __init__(self, question_schema, parent=None):
        super(MultipleChoiceQuestion, self).__init__(question_schema, parent)

    def validate(self):
        valid = super(MultipleChoiceQuestion, self).validate()

        for repetition, result in enumerate(valid):
            if self.answers[repetition] not in self.parts:
                valid[repetition].errors.append('Invalid option')


        return valid


class CheckBoxQuestion(Question):
    def __init__(self, question_schema, parent=None):
        super(CheckBoxQuestion, self).__init__(question_schema, parent)

    def validate(self):
        results = []
        for answer in self.answers:
            result = ValidationResult([], [], False)
            for item in answer:
                itemResult = self._validate_answer(item)
                result.errors += itemResult.errors
                result.warnings += itemResult.warnings
                if itemResult.accepted:
                    result.accepted = True
                results.append(result)

        return results

class InputTextQuestion(Question):
    def __init__(self, question_schema, parent=None):
        super(InputTextQuestion, self).__init__(question_schema, parent)


class DropdownQuestion(Question):
    def __init__(self, question_schema, parent=None):
        super(DropdownQuestion, self).__init__(question_schema, parent)


class TextBlock(Question):
    def __init__(self, question_schema, parent=None):
        super(TextBlock, self).__init__(question_schema, parent)

    def validate(self):
        return [ValidationResult([], [], [])]


class QuestionGroup(Question):
    def __init__(self, question_schema, parent=None):
        super(QuestionGroup, self).__init__(question_schema)
        self.children = []
        self._load_children(question_schema['children'])

    def _load_children(self, children_schema):
        for index, child in enumerate(children_schema):
            question = Question.factory(child, self)
            if not question._reference:
                question._reference = 'q' + str(index)
            self.children.append(question)

    def get_user_data(self):
        user_data = {}
        for child in self.children:
            user_data[child.get_reference()] = child.get_user_data()

        return user_data

    def validate(self):
        self.validation_results = []

        for repetition in range(0, self.repetition + 1):
            errors = []
            warnings = []
            for child in self.children:
                childValidation = child.validate()

                if len(childValidation) > repetition:
                    if not childValidation[repetition].is_valid():
                        if len(childValidation[repetition].errors) > 0:
                            errors.append(child.get_reference() + ':' + str(repetition))

                        if len(childValidation[repetition].warnings) > 0:
                            warnings.append(child.get_reference() + ':' + str(repetition))


            self.validation_results.append(ValidationResult(errors, warnings, False))

        return self.validation_results



    def branches(self):
        jumps = []
        # for child in self.children:
        #     if child.get_reference() in responses.keys():
        #         jump = child.branches(responses[child.get_reference()])
        #         if jump:
        #             jumps.append(jump)

        return jumps

    def get_branch_target(self):
        jumps = self.branches()

        # groups always branch to the first matching target

        if len(jumps) > 0:
            return jumps[0]
        else:
            return None

    def get_branch_conditions(self):
        conditions = []
        for child in self.children:
            if child.has_branch_conditions():
                child_conditions = child.get_branch_conditions()
                for child_condition in child_conditions:
                    conditions.append(child_condition)

        return conditions

    def has_branch_conditions(self):
        return len(self.get_branch_conditions()) > 0

    def get_question_by_reference(self, reference):

        address_parts = reference.split('_')
        if len(address_parts) == 1:
            for question in self.children:
                if question._reference == reference:
                    return question
        else:
            this_level = address_parts.pop(0)
            for question in self.children:
                if question._reference == this_level:
                    return question.get_question_by_reference('_'.join(address_parts))

    def _build_repeating(self, schema):
        return super(QuestionGroup, self)._build_repeating(schema)

    def set_repetition(self, repetition):
        super(QuestionGroup, self).set_repetition(repetition)
        if self.children:
            for child in self.children:
                if child:
                    child.set_repetition(repetition)