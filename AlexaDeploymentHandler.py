from AlexaBaseHandler import AlexaBaseHandler
import github
import random


class AlexaDeploymentHandler(AlexaBaseHandler):
    def __init__(self):
        super(self.__class__, self).__init__()

    def on_processing_error(self, event, context, exc):
        print("on_processing_error", event, context, exc)

    def on_session_started(self, session_started_request, session):
        print("on_session_started")

    def on_launch(self, launch_request, session):
        print("on_launch")

        return self.get_welcome_response()

    def on_session_ended(self, session_ended_request, session):
        session_attributes = {}
        speech_output = "Exiting Repo Tree."
        reprompt_text = None
        should_end_session = True

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def on_intent(self, intent_request, session):
        intent = intent_request['intent']
        intent_name = intent_request['intent']['name']
        print(intent_name)

        # Dispatch to skill's intent handlers
        if intent_name == "TopRepos":
            return self.handle_top_repo(intent_request, session)
        elif intent_name == "RepeatRepo":
            return self.handle_repeat_repo(intent_request, session)
        elif intent_name == "FeelingLucky":
            return self.handle_feeling_lucky(intent_request, session)
        elif intent_name == "AMAZON.HelpIntent":
            return self.handle_help_response()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return self.handle_session_end_request()
        else:
            raise ValueError("Invalid intent")

    def get_welcome_response(self):
        """
        Handle skill on_launch. Will repeat if user does not reply
        :return: output of _build_response
        """
        session_attributes = {}
        card_title = "Welcome"
        card_output = "Welcome to Repo Tree. " \
                      "Try asking me about the top repositories on GitHub."
        speech_output = card_output
        reprompt_text = "I didn't catch that. " \
                        "Try asking me about the top repositories on GitHub."
        should_end_session = False

        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_help_response(self):
        """
        Handle AMAZON.HelpIntent. Will provide examples
        :return: output of _build_response
        """
        session_attributes = {}
        card_title = "Help"
        card_output = \
            "Repo Tree tracks the top trending repositories on GitHub. " \
            "I can also filter them by the past day, week, month, or year in most programming languages. " \
            "For example, try asking me, what're the top repos in the past week written in Python. \n" \
            "More examples: \n" \
            "Alexa, ask Repo Tree about the top repos \n" \
            "Alexa, ask Repo Tree what're the top Python repos \n" \
            "Alexa, ask Repo Tree what're top repos in the past month \n" \
            "Alexa, ask Repo Tree about the top repos in the past week written in Java \n"
        speech_output = \
            'Repo Tree <break time="0.1s"/> tracks the top trending repositories on GitHub. ' \
            'I can also filter them by the past day, <break time="0.1s"/> week, <break time="0.1s"/> month, or year <break time="0.1s"/> in most programming languages. ' \
            'For example, try asking me, what\'re the top repos in the past week written in Python.'
        reprompt_text = "Check your Alexa app for more examples."
        should_end_session = False

        speechlet = self._build_speechlet_ssml(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_session_end_request(self):
        session_attributes = {}
        speech_output = "Exiting Repo Tree."
        reprompt_text = None
        should_end_session = True

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)

    def handle_top_repo(self, intent_request, session):
        print(intent_request)

        date = self._get_slot_value('Date', intent_request)
        language = self._get_slot_value('Language', intent_request)
        print(date, language)

        return self.create_repo_response(date, language)

    def handle_repeat_repo(self, intent_request, session):
        repeat_num = self._get_slot_value('Number', intent_request)  # str
        repeat_num = str(int(repeat_num)-1)  # account for 0 index, #1->index_0

        top_repos = self._get_attribute('top_repos', session)
        # None if user asks to repeat a number without asking for repos first
        if top_repos is None:
            return self.get_welcome_response()

        # when user asks for a number not provided earlier
        if repeat_num not in top_repos:
            return self._build_quick_response(intent_request, session, "#{0} not available".format(int(repeat_num) + 1))

        repo = top_repos[repeat_num]
        speech_output = "#{0}. Name: {1}. Description: {2}. Language: {3}. " \
            .format(int(repeat_num)+1, repo['name'],
                    repo['description'], repo['language'])

        reprompt_text = "Check your Alexa app for more details."
        should_end_session = False

        speechlet = self._build_speechlet_response_without_card(speech_output, reprompt_text, should_end_session)

        return self._build_response(session['attributes'], speechlet)

    def handle_feeling_lucky(self, intent_request, session):
        with open('LIST_OF_TIME') as date_file:
            all_date = [line.strip() for line in date_file.readlines()]
        with open('LIST_OF_PROGRAMMING_LANGUAGES') as language_file:
            all_languages = [line.strip() for line in language_file.readlines()]

        rand_date = random.choice(all_date)
        rand_language = random.choice(all_languages)
        print(rand_date, rand_language)

        return self.create_repo_response(rand_date, rand_language)

    def create_repo_response(self, date, language):
        top_repos, N_REPOS = github.get_top_repo(date_value=date, language_value=language)

        if date is None and language is None:
            date_readout = 'day'
            language_readout = ''
        elif date is None and language is not None:
            date_readout = 'day'
            language_readout = github.convert_language(language)
        elif date is not None and language is None:
            date_readout = date
            language_readout = ''
        else:
            date_readout = date
            language_readout = github.convert_language(language)

        speech_readout = "Top five {1} repos in the past {0} are, \n"\
            .format(date_readout, language_readout)
        card_readout = "Top five {1} repos in the past {0}: \n"\
            .format(date_readout, language_readout)

        for i in range(N_REPOS):
            repo = top_repos[str(i)]

            speech_readout += "#{0}. Name: {1}. Description: {2}. Language: {3}. " \
                .format(i+1, repo['name'], repo['description'], repo['language'])

            card_readout += "#{0}. {1} \n" \
                            "Description: {2} \n" \
                            "Language: {3} \n" \
                            "URL: {4} \n" \
                .format(i+1, repo['name'], repo['description'],
                        repo['language'], repo['html_url'])

        session_attributes = {'top_repos': top_repos}
        card_title = "Top 5 GitHub Repos"
        card_output = card_readout
        speech_output = speech_readout
        reprompt_text = "Check your Alexa app for more details."
        should_end_session = False

        speechlet = self._build_speechlet_response(card_title, card_output, speech_output, reprompt_text, should_end_session)

        return self._build_response(session_attributes, speechlet)
