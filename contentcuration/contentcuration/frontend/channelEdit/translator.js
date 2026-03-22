import { createTranslator } from 'shared/i18n';

const NAMESPACE = 'channelEditVue';

const MESSAGES = {
  true: 'True',
  false: 'False',
  questionTypeSingleSelection: 'Single choice',
  questionTypeMultipleSelection: 'Multiple choice',
  questionTypeOrdering: 'Ordering',
  questionTypeTrueFalse: 'True/False',
  questionTypeInput: 'Numeric input',
  questionTypePerseus: 'Perseus',
  questionTypeFreeResponse: 'Free response',
  errorQuestionRequired: 'Question is required',
  errorInvalidQuestionType: 'Invalid question type',
  errorMissingAnswer: 'Choose a correct answer',
  errorChooseAtLeastOneCorrectAnswer: 'Choose at least one correct answer',
  errorProvideAtLeastOneCorrectAnswer: 'Provide at least one correct answer',
  errorProvideAtLeastTwoAnswers: 'Provide at least two answers',
  selectionCount:
    '{topicCount, plural, =0 {} one {# folder, } other {# folders, }}{resourceCount, plural, one {# resource} other {# resources}}',
};

export default createTranslator(NAMESPACE, MESSAGES);
